import React, { useCallback, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const STATUS_META = {
  sync: {
    label: 'Syncing',
    icon: '⏳',
    title: 'Preparing Data',
    subtitle: 'Loading your latest workout and nutrition progress.'
  },
  workout: {
    label: 'Workout',
    icon: '🏋️‍♂️',
    title: 'Start Workout',
    subtitle: 'Your session is ready. Keep your streak moving.'
  },
  meal: {
    label: 'Nutrition',
    icon: '🥗',
    title: 'Complete Meals',
    subtitle: 'Log meals to hit your macros and recovery targets.'
  },
  done: {
    label: 'Completed',
    icon: '✅',
    title: 'All Set',
    subtitle: 'Great work today. Focus on hydration and sleep.'
  }
};

const STEP_TITLES = ['Workout', 'Meals', 'Recovery'];

function DashboardActionIdeas() {
  const navigate = useNavigate();
  const [status, setStatus] = useState('workout');
  const meta = STATUS_META[status];

  const score = useMemo(() => {
    if (status === 'sync') return 14;
    if (status === 'workout') return 42;
    if (status === 'meal') return 74;
    return 100;
  }, [status]);

  const workoutDone = status === 'meal' || status === 'done';
  const mealDone = status === 'done';

  const stepStatus = useMemo(() => {
    if (status === 'sync') return ['pending', 'pending', 'pending'];
    if (status === 'workout') return ['active', 'pending', 'pending'];
    if (status === 'meal') return ['done', 'active', 'pending'];
    return ['done', 'done', 'done'];
  }, [status]);

  const nextActionText =
    status === 'sync'
      ? 'Sync in progress...'
      : status === 'workout'
      ? 'Continue to Workout'
      : status === 'meal'
      ? 'Continue to Meals'
      : 'See Recovery Plan';

  const premiumCleanCard = useMemo(() => {
    if (status === 'sync') {
      return {
        eyebrow: 'Data Sync',
        headline: 'Preparing your day plan',
        body: 'We are updating workout and meal data so the next action is accurate.',
        primaryCta: 'Review readiness',
        secondaryCta: 'Open sync details',
        chips: ['Readiness --', 'Streak 7d', 'Energy calibrating']
      };
    }

    if (status === 'workout') {
      return {
        eyebrow: 'Primary Focus',
        headline: 'Strength block is ready',
        body: 'Warm-up first, then move into your top compound lift while energy is high.',
        primaryCta: 'Start strength block',
        secondaryCta: 'Preview full session',
        chips: ['Readiness 82', 'Streak 7d', 'ETA 42 min']
      };
    }

    if (status === 'meal') {
      return {
        eyebrow: 'Nutrition Focus',
        headline: 'Recovery meal pending',
        body: 'You are close to macro targets. Log one balanced meal to close the day strong.',
        primaryCta: 'Log recovery meal',
        secondaryCta: 'See meal options',
        chips: ['Protein gap 22g', 'Hydration 68%', 'ETA 5 min']
      };
    }

    return {
      eyebrow: 'Completed',
      headline: 'Strong day, keep momentum',
      body: 'Workout and nutrition are complete. Protect tomorrow with sleep and hydration.',
      primaryCta: 'Open recovery plan',
      secondaryCta: 'Review today summary',
      chips: ['Daily score 100', 'Streak 8d', 'Sleep target 8h']
    };
  }, [status]);

  const startActionAlternatives = useMemo(
    () => [
      {
        id: 'next-best-move',
        title: 'Next Best Move',
        description: 'One smart action driven by completion state and readiness.',
        fit: 'Best default for your current dashboard layout'
      },
      {
        id: 'readiness-check',
        title: 'Readiness Check',
        description: 'Shows energy and recovery score before suggesting the task.',
        fit: 'Premium look with useful data context'
      },
      {
        id: 'daily-mission',
        title: 'Daily Mission',
        description: 'One focused mission card with simple progress feedback.',
        fit: 'Clean and motivating without visual noise'
      },
      {
        id: 'quick-block',
        title: 'Quick 12-Min Block',
        description: 'Fast fallback option for low-time or low-energy moments.',
        fit: 'Improves completion rate on busy days'
      }
    ],
    []
  );

  const recommendedAlternativeId =
    status === 'sync'
      ? 'readiness-check'
      : status === 'workout'
      ? 'next-best-move'
      : status === 'meal'
      ? 'daily-mission'
      : 'quick-block';

  const coachInsight = useMemo(() => {
    if (status === 'sync') {
      return {
        title: 'AI Coach Insight',
        tip: 'Syncing your latest profile. Keep your phone nearby for posture prompts in today\'s plan.',
        action: 'Enable posture cues'
      };
    }

    if (status === 'workout') {
      return {
        title: 'AI Coach Insight',
        tip: 'Your current trend suggests higher energy in the first 25 minutes. Start with compound sets now.',
        action: 'Open warm-up sequence'
      };
    }

    if (status === 'meal') {
      return {
        title: 'AI Coach Insight',
        tip: 'Protein intake is behind target. Add one high-protein snack before dinner for better recovery.',
        action: 'See quick protein swaps'
      };
    }

    return {
      title: 'AI Coach Insight',
      tip: 'Great consistency today. A 12-minute mobility flow now can improve tomorrow\'s readiness score.',
      action: 'Start mobility flow'
    };
  }, [status]);

  const ringMetrics = useMemo(() => {
    if (status === 'sync') return { workout: 12, sleep: 28, nutrition: 18 };
    if (status === 'workout') return { workout: 64, sleep: 52, nutrition: 38 };
    if (status === 'meal') return { workout: 96, sleep: 58, nutrition: 72 };
    return { workout: 100, sleep: 92, nutrition: 94 };
  }, [status]);

  const levelData = useMemo(() => {
    const totalXp = 1850 + score * 12;
    const level = Math.max(1, Math.floor(totalXp / 250));
    const currentLevelXp = totalXp % 250;
    const xpToNext = 250 - currentLevelXp;
    const milestones = [
      { name: 'Consistency', unlocked: score >= 30 },
      { name: 'Execution', unlocked: score >= 60 },
      { name: 'Momentum', unlocked: score >= 85 }
    ];

    return {
      totalXp,
      level,
      currentLevelXp,
      xpToNext,
      milestones
    };
  }, [score]);

  const radarAxes = useMemo(
    () => ['Strength', 'Mobility', 'Endurance', 'Sleep', 'Focus', 'Recovery'],
    []
  );

  const radarMetrics = useMemo(() => {
    if (status === 'sync') return [28, 35, 24, 26, 30, 22];
    if (status === 'workout') return [72, 46, 58, 44, 70, 54];
    if (status === 'meal') return [82, 52, 68, 58, 74, 69];
    return [90, 64, 80, 88, 84, 86];
  }, [status]);

  const toRadarPoint = useCallback((idx, value, radius = 72, cx = 90, cy = 90) => {
    const angle = ((-90 + idx * (360 / radarAxes.length)) * Math.PI) / 180;
    const scaled = (value / 100) * radius;
    const x = cx + scaled * Math.cos(angle);
    const y = cy + scaled * Math.sin(angle);
    return `${x},${y}`;
  }, [radarAxes.length]);

  const radarPolygon = useMemo(
    () => radarMetrics.map((v, idx) => toRadarPoint(idx, v)).join(' '),
    [radarMetrics, toRadarPoint]
  );

  const weakestRadarAxis = useMemo(() => {
    let minIdx = 0;
    for (let i = 1; i < radarMetrics.length; i += 1) {
      if (radarMetrics[i] < radarMetrics[minIdx]) minIdx = i;
    }
    return radarAxes[minIdx];
  }, [radarAxes, radarMetrics]);

  const conceptAnimations = `
    @keyframes pulseGlow {
      0% { transform: scale(1); opacity: 0.8; }
      50% { transform: scale(1.06); opacity: 1; }
      100% { transform: scale(1); opacity: 0.8; }
    }
    @keyframes sweepRing {
      0% { filter: drop-shadow(0 0 0 rgba(99,102,241,0.2)); }
      50% { filter: drop-shadow(0 0 12px rgba(99,102,241,0.5)); }
      100% { filter: drop-shadow(0 0 0 rgba(99,102,241,0.2)); }
    }
    @keyframes previewFloat {
      0% { transform: translateY(0); }
      50% { transform: translateY(-4px); }
      100% { transform: translateY(0); }
    }
    .coach-ping {
      animation: pulseGlow 2.1s ease-in-out infinite;
    }
    .ring-glow {
      animation: sweepRing 2.3s ease-in-out infinite;
    }
    .preview-float {
      animation: previewFloat 1.8s ease-in-out infinite;
    }
    
    /* Idea 33: Universal Adaptive CSS */
    .adaptive-hero-container {
      background: linear-gradient(145deg, rgba(24, 24, 27, 0.8), rgba(9, 9, 11, 0.9));
    }
    .adaptive-desktop-view {
      display: flex;
      padding: 24px;
      gap: 20px;
      align-items: center;
      justify-content: space-between;
    }
    .adaptive-mobile-view {
      display: none;
      padding: 16px;
      border-top: 1px solid var(--app-border);
      background: rgba(9, 9, 11, 0.95);
    }
    
    @media (max-width: 768px) {
      .adaptive-desktop-view {
        display: none !important;
      }
      .adaptive-mobile-view {
        display: block !important;
      }
    }
  `;

  const ideaCard = {
    background: 'linear-gradient(160deg, rgba(39, 39, 42, 0.88) 0%, rgba(24, 24, 27, 0.92) 100%)',
    border: '1px solid rgba(161, 161, 170, 0.25)',
    borderRadius: '18px',
    padding: '18px',
    minHeight: '240px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  };

  return (
    <div
      style={{
        minHeight: '100dvh',
        background:
          'radial-gradient(circle at 10% 15%, rgba(99,102,241,0.18), transparent 28%), radial-gradient(circle at 90% 85%, rgba(236,72,153,0.16), transparent 30%), #09090b',
        color: 'var(--app-text)',
        fontFamily: "'Inter', sans-serif",
        overflowX: 'hidden'
      }}
    >
      <style>{conceptAnimations}</style>
      <header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 50,
          backdropFilter: 'blur(16px)',
          background: 'rgba(9,9,11,0.72)',
          borderBottom: '1px solid var(--app-border)',
          padding: '12px clamp(12px, 4vw, 34px)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '12px',
          flexWrap: 'wrap'
        }}
      >
        <div style={{ fontWeight: 800, fontSize: 'clamp(16px, 2.6vw, 22px)', letterSpacing: '-0.4px' }}>
          ELEVATE • Dashboard Action Concepts
        </div>
        <button
          onClick={() => navigate('/dashboard')}
          style={{
            border: '1px solid rgba(255,255,255,0.22)',
            background: 'rgba(255,255,255,0.06)',
            color: 'var(--app-text)',
            borderRadius: '12px',
            padding: '10px 14px',
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          Back to Dashboard
        </button>
      </header>

      <main style={{ width: 'min(1300px, 100%)', margin: '0 auto', padding: 'clamp(14px, 3vw, 32px)' }}>
        <section
          style={{
            background: 'linear-gradient(155deg, rgba(17,24,39,0.84) 0%, rgba(31,41,55,0.72) 100%)',
            border: '1px solid rgba(129,140,248,0.28)',
            borderRadius: '24px',
            padding: 'clamp(16px, 3vw, 28px)',
            marginBottom: '18px'
          }}
        >
          <h1 style={{ margin: 0, fontSize: 'clamp(24px, 4.8vw, 36px)' }}>Action Box Playground</h1>
          <p style={{ margin: '10px 0 16px', color: '#c4b5fd', lineHeight: 1.6 }}>
            This is a copy-preview page with only the first Dashboard action area and all ideas in one file.
            Use the status switch below to preview each design state.
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {Object.entries(STATUS_META).map(([key, value]) => {
              const active = key === status;
              return (
                <button
                  key={key}
                  onClick={() => setStatus(key)}
                  style={{
                    border: active ? '1px solid rgba(129,140,248,0.65)' : '1px solid rgba(255,255,255,0.18)',
                    background: active ? 'rgba(79,70,229,0.28)' : 'var(--app-border)',
                    color: 'var(--app-text)',
                    borderRadius: '999px',
                    padding: '8px 14px',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  {value.icon} {value.label}
                </button>
              );
            })}
          </div>
        </section>

        <section
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '14px'
          }}
        >
          <article style={ideaCard}>
            <h3 style={{ margin: 0 }}>1) Today Flow Stepper</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>Clear progress with one primary Continue button.</p>
            <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
              {STEP_TITLES.map((title, i) => {
                const state = stepStatus[i];
                const bg = state === 'done' ? '#16a34a' : state === 'active' ? '#4f46e5' : '#3f3f46';
                return (
                  <div key={title} style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        width: '100%',
                        borderRadius: '999px',
                        height: '8px',
                        background: bg,
                        marginBottom: '6px'
                      }}
                    />
                    <div style={{ fontSize: '12px', color: '#d4d4d8' }}>{title}</div>
                  </div>
                );
              })}
            </div>
            <button
              style={{
                marginTop: 'auto',
                border: 'none',
                borderRadius: '12px',
                background: status === 'sync' ? '#3f3f46' : '#4f46e5',
                color: 'var(--app-text)',
                padding: '12px',
                fontWeight: 700,
                cursor: status === 'sync' ? 'default' : 'pointer'
              }}
              disabled={status === 'sync'}
            >
              {nextActionText}
            </button>
          </article>

          <article style={ideaCard}>
            <h3 style={{ margin: 0 }}>2) Two Action Tiles + Banner</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>Two clear tasks until complete, then success banner.</p>
            {status === 'done' ? (
              <div
                style={{
                  marginTop: '6px',
                  border: '1px solid rgba(74,222,128,0.4)',
                  background: 'rgba(22,163,74,0.12)',
                  borderRadius: '14px',
                  padding: '14px',
                  color: '#bbf7d0',
                  fontWeight: 700
                }}
              >
                ✅ Daily mission complete. Keep hydration and sleep on track.
              </div>
            ) : (
              <>
                <div
                  style={{
                    border: '1px solid rgba(129,140,248,0.34)',
                    background: workoutDone ? 'rgba(34,197,94,0.14)' : 'rgba(79,70,229,0.15)',
                    borderRadius: '12px',
                    padding: '12px'
                  }}
                >
                  💪 Workout {workoutDone ? 'Done' : 'Pending'}
                </div>
                <div
                  style={{
                    border: '1px solid rgba(244,114,182,0.34)',
                    background: mealDone ? 'rgba(34,197,94,0.14)' : 'rgba(236,72,153,0.15)',
                    borderRadius: '12px',
                    padding: '12px'
                  }}
                >
                  🥗 Meals {mealDone ? 'Done' : 'Pending'}
                </div>
              </>
            )}
          </article>

          <article style={ideaCard}>
            <h3 style={{ margin: 0 }}>3) Next Best Action Card</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>One smart action instead of multiple competing CTAs.</p>
            <div
              style={{
                marginTop: '6px',
                border: '1px solid rgba(255,255,255,0.22)',
                background: 'linear-gradient(145deg, rgba(79,70,229,0.28) 0%, rgba(15,23,42,0.7) 100%)',
                borderRadius: '16px',
                padding: '14px',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px'
              }}
            >
              <div style={{ fontSize: '12px', color: '#a5b4fc', fontWeight: 700, textTransform: 'uppercase' }}>
                Next Best Action
              </div>
              <div style={{ fontSize: '20px', fontWeight: 800 }}>
                {meta.icon} {meta.title}
              </div>
              <div style={{ fontSize: '13px', color: '#d4d4d8' }}>{meta.subtitle}</div>
            </div>
            <button
              style={{
                marginTop: 'auto',
                border: '1px solid rgba(255,255,255,0.18)',
                borderRadius: '12px',
                background: 'var(--app-surface)',
                color: 'var(--app-text)',
                padding: '11px',
                fontWeight: 700,
                cursor: 'pointer'
              }}
            >
              Open Suggested Task
            </button>
          </article>

          <article style={ideaCard}>
            <h3 style={{ margin: 0 }}>4) Mission Timeline</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>Timeline format for users who like a daily mission journey.</p>
            <div style={{ marginTop: '8px', display: 'grid', gap: '10px' }}>
              {[
                { key: 'workout', text: 'Workout Block' },
                { key: 'meal', text: 'Nutrition Block' },
                { key: 'done', text: 'Recovery Block' }
              ].map((item, idx) => {
                const st = stepStatus[idx];
                const dot = st === 'done' ? '✅' : st === 'active' ? '🟣' : '⚪';
                return (
                  <div key={item.key} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span>{dot}</span>
                    <span style={{ fontSize: '13px', color: 'var(--app-text)' }}>{item.text}</span>
                  </div>
                );
              })}
            </div>
          </article>

          <article style={ideaCard}>
            <h3 style={{ margin: 0 }}>5) Sticky Command Bar</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>Great for mobile: one primary action + two quick actions.</p>
            <div style={{ flex: 1 }} />
            <div
              style={{
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '14px',
                padding: '10px',
                background: 'rgba(9,9,11,0.7)',
                display: 'grid',
                gridTemplateColumns: '1fr auto auto',
                gap: '8px',
                alignItems: 'center'
              }}
            >
              <button style={{ border: 'none', borderRadius: '10px', padding: '10px', background: '#4f46e5', color: 'var(--app-text)', fontWeight: 700 }}>
                {meta.icon} {meta.title}
              </button>
              <button style={{ border: '1px solid rgba(255,255,255,0.25)', borderRadius: '10px', background: 'transparent', color: 'var(--app-text)', padding: '10px' }}>
                💧
              </button>
              <button style={{ border: '1px solid rgba(255,255,255,0.25)', borderRadius: '10px', background: 'transparent', color: 'var(--app-text)', padding: '10px' }}>
                😴
              </button>
            </div>
          </article>

          <article style={ideaCard}>
            <h3 style={{ margin: 0 }}>6) Score-Based Action Hub</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>Drive behavior with one daily score + top priorities.</p>
            <div style={{ display: 'flex', gap: '14px', alignItems: 'center', marginTop: '4px' }}>
              <div
                style={{
                  width: '86px',
                  height: '86px',
                  borderRadius: '50%',
                  background: `conic-gradient(#4f46e5 ${score}%, rgba(255,255,255,0.12) ${score}% 100%)`,
                  display: 'grid',
                  placeItems: 'center'
                }}
              >
                <div
                  style={{
                    width: '64px',
                    height: '64px',
                    borderRadius: '50%',
                    background: '#0f0f12',
                    display: 'grid',
                    placeItems: 'center',
                    fontWeight: 800,
                    color: 'var(--app-text)'
                  }}
                >
                  {score}
                </div>
              </div>
              <div style={{ fontSize: '13px', color: '#d4d4d8' }}>
                <div>Daily Score</div>
                <div style={{ color: 'var(--app-text-muted)', marginTop: '4px' }}>{meta.title}</div>
              </div>
            </div>
            <ul style={{ margin: '10px 0 0', paddingLeft: '18px', color: '#cbd5e1', fontSize: '13px', lineHeight: 1.5 }}>
              <li>Top priority: {meta.title}</li>
              <li>Secondary: Hydration and sleep</li>
              <li>Reward: streak boost on completion</li>
            </ul>
          </article>

          <article style={{
            ...ideaCard,
            background: 'rgba(15, 23, 42, 0.4)',
            backdropFilter: 'blur(24px)',
            border: '1px solid var(--app-border)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{
              position: 'absolute',
              top: '-50px',
              right: '-50px',
              width: '150px',
              height: '150px',
              background: 'radial-gradient(circle, rgba(99,102,241,0.4) 0%, transparent 70%)',
              filter: 'blur(30px)',
              zIndex: 0
            }} />
            <div style={{ zIndex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
              <h3 style={{ margin: 0, color: 'var(--app-text)', textShadow: '0 0 10px rgba(255,255,255,0.2)' }}>7) Glassmorphic Pulse</h3>
              <p style={{ margin: '4px 0 0', color: '#94a3b8', fontSize: '13px' }}>Premium blurred aesthetics with glowing accents.</p>
              
              <div style={{ margin: 'auto 0', display: 'flex', alignItems: 'center', gap: '16px', background: 'var(--quote-bg)', padding: '16px', borderRadius: '16px', border: '1px solid var(--app-border)' }}>
                <div style={{ fontSize: '32px' }}>{meta.icon}</div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '16px', color: '#e0e7ff' }}>{meta.title}</div>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>Ready when you are</div>
                </div>
              </div>

              <button style={{
                marginTop: '16px',
                width: '100%',
                padding: '12px',
                borderRadius: '12px',
                background: 'linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%)',
                color: 'white',
                border: 'none',
                fontWeight: 700,
                cursor: 'pointer',
                boxShadow: '0 4px 15px rgba(79, 70, 229, 0.3)'
              }}>
                Launch {meta.label}
              </button>
            </div>
          </article>

          <article style={{ ...ideaCard, alignItems: 'center', textAlign: 'center', justifyContent: 'center' }}>
            <h3 style={{ margin: 0, alignSelf: 'flex-start' }}>8) Neon Radial Focus</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px', alignSelf: 'flex-start' }}>Activity ring style single ring focus.</p>
            
            <div style={{
              width: '120px',
              height: '120px',
              borderRadius: '50%',
              background: `conic-gradient(#ec4899 ${score}%, var(--app-border) ${score}% 100%)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '16px 0',
              boxShadow: '0 0 20px rgba(236, 72, 153, 0.2)'
            }}>
              <div style={{
                width: '100px',
                height: '100px',
                borderRadius: '50%',
                background: 'var(--app-surface)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <div style={{ fontSize: '24px' }}>{meta.icon}</div>
                <div style={{ fontWeight: 800, color: '#fce7f3' }}>{score}%</div>
              </div>
            </div>
            
            <button style={{
              width: '100%',
              padding: '10px',
              borderRadius: '999px',
              border: '2px solid #ec4899',
              background: 'transparent',
              color: '#ec4899',
              fontWeight: 700,
              cursor: 'pointer'
            }}>
              {meta.title} →
            </button>
          </article>

          <article style={{
            ...ideaCard,
            background: 'var(--app-bg)',
            backgroundImage: 'radial-gradient(circle at 50% 0%, rgba(245, 158, 11, 0.15), transparent 60%)',
            border: '1px solid rgba(245, 158, 11, 0.2)'
          }}>
            <h3 style={{ margin: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              9) Gamified Journey
              <span style={{ fontSize: '12px', background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', padding: '4px 8px', borderRadius: '999px', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
                🔥 7 Day Streak
              </span>
            </h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>Focuses on rewarding consistency and progression.</p>
            
            <div style={{ margin: 'auto 0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#d4d4d8', marginBottom: '8px' }}>
                <span style={{ fontWeight: 600 }}>Level 12 Explorer</span>
                <span style={{ color: '#fbbf24', fontWeight: 600 }}>{score} / 100 XP</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: 'var(--app-border)', borderRadius: '999px', overflow: 'hidden' }}>
                <div style={{ width: `${score}%`, height: '100%', background: 'linear-gradient(90deg, #f59e0b, #ef4444)', borderRadius: '999px' }} />
              </div>
            </div>
            
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              background: 'var(--quote-bg)',
              padding: '12px',
              borderRadius: '12px',
              border: '1px solid var(--app-border)'
            }}>
              <div style={{ fontSize: '24px' }}>{meta.icon}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '14px', fontWeight: 700, color: '#fafafa' }}>{meta.title}</div>
                <div style={{ fontSize: '12px', color: 'var(--app-text-muted)' }}>+ 25 XP</div>
              </div>
              <button style={{
                background: 'linear-gradient(135deg, #f59e0b, #ea580c)',
                border: 'none',
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                color: 'var(--app-text)',
                fontWeight: 800,
                cursor: 'pointer',
                display: 'grid',
                placeItems: 'center',
                boxShadow: '0 2px 10px rgba(245, 158, 11, 0.3)'
              }}>
                ▶
              </button>
            </div>
          </article>

          <article style={{ ...ideaCard, background: 'var(--app-bg)', border: '1px solid var(--app-border)', borderRadius: '4px' }}>
            <h3 style={{ margin: 0, color: '#52525b', fontWeight: 500, fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px' }}>
              10) Editorial Minimal
            </h3>
            <p style={{ margin: '8px 0 0', color: '#71717a', fontSize: '13px', lineHeight: 1.5 }}>
              Ultra clean. Relies on large typography and high contrast instead of borders or containers.
            </p>
            
            <div style={{ margin: 'auto 0' }}>
              <div style={{ color: 'var(--app-text)', fontSize: 'clamp(28px, 3vw, 34px)', fontWeight: 300, letterSpacing: '-1px', lineHeight: 1.1 }}>
                Time for your<br />
                <span style={{ fontWeight: 700, fontStyle: 'italic', background: 'linear-gradient(90deg, #fff, #a1a1aa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>{meta.label}.</span>
              </div>
            </div>
            
            <button style={{
              marginTop: '16px',
              padding: '14px 20px',
              background: 'var(--app-text)',
              color: 'var(--app-text)',
              border: 'none',
              borderRadius: '2px',
              fontWeight: 800,
              fontSize: '14px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              boxShadow: '0 4px 14px var(--app-border)'
            }}>
              {meta.title}
              <span style={{ fontSize: '16px' }}>→</span>
            </button>
          </article>

          <article style={{ ...ideaCard, border: '1px solid rgba(99,102,241,0.28)' }}>
            <h3 style={{ margin: 0 }}>11) AI Coach Insight</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>
              Replaces a generic start button with instant, specific coaching value.
            </p>
            <div
              className="coach-ping"
              style={{
                marginTop: '8px',
                border: '1px solid rgba(129,140,248,0.35)',
                background: 'linear-gradient(145deg, rgba(79,70,229,0.2), rgba(15,23,42,0.7))',
                borderRadius: '14px',
                padding: '12px'
              }}
            >
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#a5b4fc', fontWeight: 700 }}>
                {coachInsight.title}
              </div>
              <div style={{ marginTop: '8px', fontSize: '13px', color: '#e0e7ff', lineHeight: 1.5 }}>
                {coachInsight.tip}
              </div>
            </div>
            <button
              style={{
                marginTop: 'auto',
                border: '1px solid rgba(99,102,241,0.45)',
                background: 'rgba(99,102,241,0.15)',
                color: '#c7d2fe',
                borderRadius: '12px',
                padding: '10px',
                fontWeight: 700,
                cursor: 'pointer'
              }}
            >
              {coachInsight.action}
            </button>
          </article>

          <article style={{ ...ideaCard, border: '1px solid rgba(56,189,248,0.26)' }}>
            <h3 style={{ margin: 0 }}>12) Dynamic Glowing Rings</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>
              Concentric score rings for Workout, Sleep, and Nutrition in one glance.
            </p>
            <div style={{ flex: 1, display: 'grid', placeItems: 'center', marginTop: '8px' }}>
              <div
                className="ring-glow"
                style={{
                  width: '168px',
                  height: '168px',
                  borderRadius: '50%',
                  background: `conic-gradient(#4f46e5 ${ringMetrics.workout}%, var(--app-border) ${ringMetrics.workout}% 100%)`,
                  display: 'grid',
                  placeItems: 'center'
                }}
              >
                <div
                  style={{
                    width: '128px',
                    height: '128px',
                    borderRadius: '50%',
                    background: `conic-gradient(#06b6d4 ${ringMetrics.sleep}%, var(--app-border) ${ringMetrics.sleep}% 100%)`,
                    display: 'grid',
                    placeItems: 'center'
                  }}
                >
                  <div
                    style={{
                      width: '90px',
                      height: '90px',
                      borderRadius: '50%',
                      background: `conic-gradient(#ec4899 ${ringMetrics.nutrition}%, var(--app-border) ${ringMetrics.nutrition}% 100%)`,
                      display: 'grid',
                      placeItems: 'center'
                    }}
                  >
                    <div
                      style={{
                        width: '58px',
                        height: '58px',
                        borderRadius: '50%',
                        background: '#0f172a',
                        display: 'grid',
                        placeItems: 'center',
                        color: 'var(--app-text)',
                        fontWeight: 800,
                        fontSize: '12px'
                      }}
                    >
                      {score}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#cbd5e1' }}>
              <span>Workout {ringMetrics.workout}%</span>
              <span>Sleep {ringMetrics.sleep}%</span>
              <span>Nutrition {ringMetrics.nutrition}%</span>
            </div>
          </article>

          <article style={{ ...ideaCard, border: '1px solid rgba(34,197,94,0.24)' }}>
            <h3 style={{ margin: 0 }}>13) Animated Workout Preview</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>
              Movement-first CTA that communicates today&apos;s workout instantly.
            </p>
            <div
              style={{
                flex: 1,
                marginTop: '8px',
                borderRadius: '16px',
                border: '1px solid rgba(74,222,128,0.2)',
                background: 'radial-gradient(circle at 50% 15%, rgba(34,197,94,0.2), rgba(15,23,42,0.9) 65%)',
                display: 'grid',
                placeItems: 'center'
              }}
            >
              <svg className="preview-float" width="170" height="120" viewBox="0 0 170 120" role="img" aria-label="Workout movement preview">
                <rect x="8" y="8" width="154" height="104" rx="14" fill="none" stroke="rgba(187,247,208,0.4)" />
                <circle cx="85" cy="30" r="10" fill="#86efac">
                  <animate attributeName="cy" values="30;27;30" dur="1.1s" repeatCount="indefinite" />
                </circle>
                <line x1="85" y1="40" x2="85" y2="70" stroke="#4ade80" strokeWidth="6" strokeLinecap="round" />
                <line x1="85" y1="48" x2="62" y2="64" stroke="#4ade80" strokeWidth="6" strokeLinecap="round" />
                <line x1="85" y1="48" x2="108" y2="64" stroke="#4ade80" strokeWidth="6" strokeLinecap="round" />
                <line x1="85" y1="70" x2="68" y2="95" stroke="#4ade80" strokeWidth="6" strokeLinecap="round">
                  <animate attributeName="y2" values="95;88;95" dur="1.1s" repeatCount="indefinite" />
                </line>
                <line x1="85" y1="70" x2="102" y2="95" stroke="#4ade80" strokeWidth="6" strokeLinecap="round">
                  <animate attributeName="y2" values="95;102;95" dur="1.1s" repeatCount="indefinite" />
                </line>
              </svg>
            </div>
            <button style={{ marginTop: 'auto', padding: '11px', borderRadius: '12px', border: 'none', background: '#16a34a', color: 'var(--app-text)', fontWeight: 700, cursor: 'pointer' }}>
              Start {meta.title}
            </button>
          </article>

          <article style={{ ...ideaCard, border: '1px solid rgba(251,191,36,0.28)' }}>
            <h3 style={{ margin: 0 }}>14) Gamified Level-Up</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>
              Progress visibility with XP, level milestones, and next unlock.
            </p>
            <div style={{ marginTop: '8px', display: 'grid', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '13px', color: '#fcd34d', fontWeight: 700 }}>Level {levelData.level}</span>
                <span style={{ fontSize: '12px', color: '#fde68a' }}>{levelData.totalXp} XP total</span>
              </div>
              <div style={{ height: '8px', borderRadius: '999px', background: 'var(--app-border)', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${(levelData.currentLevelXp / 250) * 100}%`,
                    height: '100%',
                    background: 'linear-gradient(90deg, #f59e0b, #f97316)',
                    borderRadius: '999px'
                  }}
                />
              </div>
              <div style={{ fontSize: '12px', color: 'var(--app-text-muted)' }}>{levelData.xpToNext} XP to next level</div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {levelData.milestones.map((m) => (
                  <span
                    key={m.name}
                    style={{
                      fontSize: '11px',
                      borderRadius: '999px',
                      padding: '5px 9px',
                      background: m.unlocked ? 'rgba(34,197,94,0.2)' : 'rgba(255,255,255,0.07)',
                      color: m.unlocked ? '#bbf7d0' : '#cbd5e1',
                      border: m.unlocked ? '1px solid rgba(34,197,94,0.35)' : '1px solid rgba(255,255,255,0.14)'
                    }}
                  >
                    {m.unlocked ? '✓ ' : ''}
                    {m.name}
                  </span>
                ))}
              </div>
            </div>
          </article>

          <article style={{ ...ideaCard, border: '1px solid rgba(45,212,191,0.28)' }}>
            <h3 style={{ margin: 0 }}>15) Physical Balance Radar Chart</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>
              Multi-axis wellness map to identify today&apos;s weakest area and focus goal.
            </p>
            <div style={{ marginTop: '4px', display: 'grid', placeItems: 'center' }}>
              <svg width="180" height="180" viewBox="0 0 180 180" role="img" aria-label="Physical balance radar chart">
                {[25, 50, 75, 100].map((scale) => (
                  <polygon
                    key={scale}
                    points={radarAxes.map((_, idx) => toRadarPoint(idx, scale)).join(' ')}
                    fill="none"
                    stroke="rgba(148,163,184,0.25)"
                    strokeWidth="1"
                  />
                ))}
                {radarAxes.map((axis, idx) => {
                  const [x, y] = toRadarPoint(idx, 100).split(',');
                  const [lx, ly] = toRadarPoint(idx, 116).split(',');
                  return (
                    <g key={axis}>
                      <line x1="90" y1="90" x2={x} y2={y} stroke="rgba(148,163,184,0.25)" strokeWidth="1" />
                      <text x={lx} y={ly} fill="#94a3b8" fontSize="9" textAnchor="middle" dominantBaseline="middle">
                        {axis}
                      </text>
                    </g>
                  );
                })}
                <polygon points={radarPolygon} fill="rgba(45,212,191,0.28)" stroke="#2dd4bf" strokeWidth="2" />
                {radarMetrics.map((v, idx) => {
                  const [x, y] = toRadarPoint(idx, v).split(',');
                  return <circle key={`${radarAxes[idx]}-${v}`} cx={x} cy={y} r="2.7" fill="#5eead4" />;
                })}
              </svg>
            </div>
            <div style={{ marginTop: 'auto', fontSize: '12px', color: '#99f6e4' }}>
              Focus suggestion: <strong>{weakestRadarAxis}</strong>
            </div>
          </article>

          <article style={{ ...ideaCard, background: '#05070c', border: '1px solid rgba(255,255,255,0.16)' }}>
            <h3 style={{ margin: 0 }}>16) Minimalist Oversized Typography</h3>
            <p style={{ margin: 0, color: '#71717a', fontSize: '13px' }}>
              Single, powerful call to action with strong editorial rhythm.
            </p>
            <div style={{ margin: 'auto 0' }}>
              <div style={{ fontSize: 'clamp(30px, 4vw, 44px)', color: 'var(--app-text)', fontWeight: 300, lineHeight: 1.04, letterSpacing: '-1px' }}>
                {status === 'done' ? 'You are done.' : 'Go train now.'}
              </div>
              <div style={{ marginTop: '8px', fontSize: 'clamp(18px, 2.6vw, 28px)', color: 'var(--app-text-muted)', fontWeight: 700 }}>
                {meta.title.toUpperCase()}
              </div>
            </div>
            <button
              style={{
                marginTop: '16px',
                border: 'none',
                borderRadius: '0',
                padding: '12px 14px',
                background: 'var(--app-text)',
                color: 'var(--app-text)',
                fontWeight: 800,
                letterSpacing: '0.7px',
                cursor: 'pointer'
              }}
            >
              {meta.title} →
            </button>
          </article>

          <article style={ideaCard}>
            <h3 style={{ margin: 0 }}>17) Habit Heatmap Calendar</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>
              A monthly visual streak map that highlights consistency at a glance.
            </p>
            <div style={{ marginTop: '8px', display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '4px' }}>
              {Array.from({ length: 28 }).map((_, i) => {
                const intensity = (i * 13 + score) % 100;
                const color = intensity > 75 ? 'rgba(34,197,94,0.82)' : intensity > 45 ? 'rgba(59,130,246,0.72)' : intensity > 20 ? 'rgba(251,191,36,0.62)' : 'rgba(63,63,70,0.7)';
                return <div key={i} style={{ height: '16px', borderRadius: '3px', background: color }} />;
              })}
            </div>
          </article>

          <article style={ideaCard}>
            <h3 style={{ margin: 0 }}>18) Adaptive Micro-Challenges</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>
              AI-generated mini goals tailored to today&apos;s readiness and backlog.
            </p>
            <div style={{ marginTop: '8px', display: 'grid', gap: '8px' }}>
              {[
                `Complete 2 focus sets in first 20 minutes`,
                `Add 25g protein before 7 PM`,
                `Log 600ml water in next 45 min`
              ].map((item) => (
                <div key={item} style={{ border: '1px solid rgba(255,255,255,0.14)', borderRadius: '10px', padding: '9px 10px', fontSize: '12px', color: '#e2e8f0', background: 'var(--quote-bg)' }}>
                  🎯 {item}
                </div>
              ))}
            </div>
          </article>

          <article style={ideaCard}>
            <h3 style={{ margin: 0 }}>19) Focus Mode Countdown Capsule</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>
              A single immersive countdown capsule to lock users into the next task.
            </p>
            <div style={{ flex: 1, display: 'grid', placeItems: 'center', marginTop: '8px' }}>
              <div style={{ width: '190px', borderRadius: '999px', border: '1px solid rgba(129,140,248,0.4)', padding: '8px', background: 'rgba(79,70,229,0.14)' }}>
                <div style={{ borderRadius: '999px', background: '#0f172a', color: '#c7d2fe', padding: '10px', textAlign: 'center', fontWeight: 800, letterSpacing: '1px' }}>
                  00:14:32
                </div>
              </div>
            </div>
            <button style={{ marginTop: 'auto', border: 'none', borderRadius: '12px', padding: '11px', background: '#4f46e5', color: 'var(--app-text)', fontWeight: 700, cursor: 'pointer' }}>
              Enter Focus Mode
            </button>
          </article>

          <article style={{
            ...ideaCard,
            padding: '12px',
            background: 'var(--app-bg)',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gridTemplateRows: 'auto 1fr',
            gap: '8px'
          }}>
            <div style={{ gridColumn: '1 / -1', padding: '4px 8px' }}>
               <h3 style={{ margin: 0, fontSize: '14px', color: 'var(--app-text)' }}>20) Bento Action Hub</h3>
               <p style={{ margin: '4px 0 0', color: 'var(--app-text-muted)', fontSize: '12px' }}>Modular layout packed with context.</p>
            </div>
            
            <div style={{
              gridColumn: '1 / -1',
              background: 'var(--app-surface2)',
              borderRadius: '12px',
              padding: '16px',
              border: '1px solid #3f3f46',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              cursor: 'pointer'
            }}>
              <div style={{ fontSize: '36px', marginBottom: '8px' }}>{meta.icon}</div>
              <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--app-text)' }}>{meta.title}</div>
              <div style={{ fontSize: '12px', color: 'var(--app-text-muted)', marginTop: '4px' }}>Primary Action</div>
            </div>

            <div style={{
              background: 'rgba(56, 189, 248, 0.1)',
              border: '1px solid rgba(56, 189, 248, 0.2)',
              borderRadius: '12px',
              padding: '12px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}>
              <div style={{ fontSize: '18px' }}>💧</div>
              <div>
                <div style={{ color: '#bae6fd', fontWeight: 700, fontSize: '14px' }}>2.4L</div>
                <div style={{ color: '#7dd3fc', fontSize: '11px' }}>Hydration</div>
              </div>
            </div>

            <div style={{
              background: 'rgba(250, 204, 21, 0.1)',
              border: '1px solid rgba(250, 204, 21, 0.2)',
              borderRadius: '12px',
              padding: '12px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}>
              <div style={{ fontSize: '18px' }}>⚡</div>
              <div>
                <div style={{ color: '#fef08a', fontWeight: 700, fontSize: '14px' }}>850</div>
                <div style={{ color: '#fde047', fontSize: '11px' }}>Kcal Burn</div>
              </div>
            </div>
          </article>

          <article style={{ ...ideaCard, background: '#111827', border: '1px solid #1f2937' }}>
            <h3 style={{ margin: 0 }}>21) Slide to Confirm</h3>
            <p style={{ margin: 0, color: '#9ca3af', fontSize: '13px' }}>Engaging physical interaction style heavily used in fitness apps.</p>
            
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <div style={{ fontSize: '48px', textAlign: 'center', marginBottom: '16px' }}>{meta.icon}</div>
              <div style={{ textAlign: 'center', fontSize: '20px', fontWeight: 700, color: '#f3f4f6' }}>{meta.title}</div>
              <div style={{ textAlign: 'center', fontSize: '13px', color: '#9ca3af' }}>{meta.subtitle}</div>
            </div>

            <div style={{
              background: '#1f2937',
              borderRadius: '999px',
              padding: '6px',
              display: 'flex',
              alignItems: 'center',
              position: 'relative',
              overflow: 'hidden',
              marginTop: '16px'
            }}>
              <div style={{
                background: '#4f46e5',
                width: '46px',
                height: '46px',
                borderRadius: '50%',
                display: 'grid',
                placeItems: 'center',
                color: 'var(--app-text)',
                fontSize: '18px',
                zIndex: 2,
                boxShadow: '0 4px 10px rgba(0,0,0,0.3)',
                position: 'relative',
                left: '0px'
              }}>
                »
              </div>
              <div style={{
                position: 'absolute',
                width: '100%',
                textAlign: 'center',
                color: '#9ca3af',
                fontSize: '14px',
                fontWeight: 600,
                letterSpacing: '0.5px',
                zIndex: 1
              }}>
                Slide to Start
              </div>
            </div>
          </article>

          <article style={{ ...ideaCard, background: 'var(--app-surface)' }}>
            <h3 style={{ margin: 0 }}>22) Intelligent Context</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>Explains *why* this is the action, using mini-data visualizations.</p>
            
            <div style={{ marginTop: '16px', background: 'var(--app-surface2)', borderRadius: '12px', padding: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'flex-end', height: '40px', gap: '6px', marginBottom: '8px' }}>
                <div style={{ flex: 1, background: '#3f3f46', height: '40%', borderRadius: '4px' }} />
                <div style={{ flex: 1, background: '#3f3f46', height: '60%', borderRadius: '4px' }} />
                <div style={{ flex: 1, background: '#3f3f46', height: '30%', borderRadius: '4px' }} />
                <div style={{ flex: 1, background: '#10b981', height: '90%', borderRadius: '4px', position: 'relative' }}>
                   <div style={{ position: 'absolute', top: '-14px', left: '50%', transform: 'translateX(-50%)', fontSize: '10px', color: '#10b981', fontWeight: 800 }}>8h</div>
                </div>
              </div>
              <p style={{ margin: 0, fontSize: '12px', color: '#d4d4d8', lineHeight: 1.4 }}>
                <strong style={{ color: '#10b981' }}>Great recovery!</strong> 8h of sleep detected. You are primed for high-intensity output today.
              </p>
            </div>
            
            <div style={{ flex: 1 }} />
            
            <button style={{
              marginTop: '16px',
              padding: '14px',
              background: 'var(--app-text)',
              color: 'var(--app-text)',
              border: 'none',
              borderRadius: '12px',
              fontWeight: 800,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}>
              {meta.icon} {meta.title}
            </button>
          </article>

          <article style={{
            ...ideaCard,
            background: 'transparent',
            border: 'none',
            padding: 0,
            overflow: 'visible'
          }}>
            <div style={{
              background: 'var(--app-surface)',
              borderRadius: '24px',
              padding: '24px',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: 'inset 0 1px 0 0 var(--app-border), 0 20px 40px -10px rgba(0,0,0,0.8), 0 0 40px -10px rgba(99,102,241,0.15)',
              position: 'relative'
            }}>
              <h3 style={{ margin: 0, color: 'var(--app-text)', fontSize: '15px' }}>23) Floating Neumorphic</h3>
              <p style={{ margin: 0, color: '#71717a', fontSize: '13px' }}>Rich shadows and inset lighting create a tactile feel.</p>
              
              <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  borderRadius: '20px',
                  background: 'var(--app-surface2)',
                  boxShadow: '4px 4px 10px rgba(0,0,0,0.5), -4px -4px 10px rgba(255,255,255,0.03), inset 1px 1px 0px var(--app-border)',
                  display: 'grid',
                  placeItems: 'center',
                  fontSize: '36px'
                }}>
                  {meta.icon}
                </div>
              </div>
              
              <button style={{
                background: 'linear-gradient(180deg, #4f46e5 0%, #4338ca 100%)',
                color: 'var(--app-text)',
                border: 'none',
                borderRadius: '14px',
                padding: '14px',
                fontWeight: 700,
                fontSize: '15px',
                boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.2), 0 8px 16px -4px rgba(79,70,229,0.5)',
                cursor: 'pointer',
                textShadow: '0 1px 2px rgba(0,0,0,0.2)'
              }}>
                {meta.title}
              </button>
            </div>
          </article>

          <article style={ideaCard}>
            <h3 style={{ margin: 0, color: 'var(--app-text)' }}>24) Body Readiness Score</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>Focuses on recovery capacity rather than the workout itself.</p>
            
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '20px', marginTop: '16px' }}>
              <div style={{
                position: 'relative',
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: `conic-gradient(#10b981 85%, #27272a 85% 100%)`,
                display: 'grid',
                placeItems: 'center',
                boxShadow: '0 0 20px rgba(16, 185, 129, 0.2)'
              }}>
                <div style={{ width: '66px', height: '66px', borderRadius: '50%', background: 'var(--app-surface)', display: 'grid', placeItems: 'center' }}>
                  <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--app-text)' }}>85</span>
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <span style={{ color: '#34d399', fontWeight: 700, fontSize: '15px' }}>Prime Condition</span>
                <span style={{ color: 'var(--app-text-muted)', fontSize: '12px' }}>Heart rate variability is optimal.</span>
              </div>
            </div>

            <button style={{ marginTop: 'auto', border: '1px solid rgba(16, 185, 129, 0.3)', background: 'rgba(16, 185, 129, 0.1)', color: '#6ee7b7', borderRadius: '12px', padding: '12px', fontWeight: 700, cursor: 'pointer', transition: 'all 0.2s' }}>
              View Recovery Metrics
            </button>
          </article>

          <article style={{ ...ideaCard, background: 'linear-gradient(160deg, #18181b 0%, #0f172a 100%)', border: '1px solid #1e293b' }}>
            <h3 style={{ margin: 0, color: 'var(--app-text)' }}>25) Macronutrient Gap</h3>
            <p style={{ margin: 0, color: '#94a3b8', fontSize: '13px' }}>Highlights the most critical missing nutritional element.</p>
            
            <div style={{ margin: 'auto 0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '12px' }}>
                <div>
                  <div style={{ color: '#f8fafc', fontSize: '24px', fontWeight: 800 }}>45g</div>
                  <div style={{ color: '#60a5fa', fontSize: '12px', fontWeight: 700, textTransform: 'uppercase' }}>Protein Remaining</div>
                </div>
                <div style={{ fontSize: '32px' }}>🥩</div>
              </div>
              
              <div style={{ width: '100%', height: '6px', background: '#1e293b', borderRadius: '999px', overflow: 'hidden' }}>
                <div style={{ width: '65%', height: '100%', background: '#3b82f6', borderRadius: '999px' }} />
              </div>
              <div style={{ color: '#64748b', fontSize: '11px', marginTop: '6px', textAlign: 'right' }}>105 / 150g Consumed</div>
            </div>

            <button style={{ border: 'none', background: '#3b82f6', color: 'var(--app-text)', borderRadius: '12px', padding: '12px', fontWeight: 700, cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}>
              <span>+</span> Log High-Protein Meal
            </button>
          </article>

          <article style={{ ...ideaCard, background: 'var(--app-bg)', backgroundImage: 'radial-gradient(circle at 100% 0%, rgba(244, 63, 94, 0.1), transparent 50%)' }}>
            <h3 style={{ margin: 0, color: 'var(--app-text)' }}>26) Daily Micro-Challenge</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>Replaces overwhelming tasks with one highly achievable micro-goal.</p>
            
            <div style={{ margin: 'auto 0', padding: '16px', background: 'var(--quote-bg)', borderRadius: '16px', border: '1px dashed rgba(244, 63, 94, 0.3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ fontSize: '28px' }}>🧘</div>
                <div>
                  <div style={{ color: '#fb7185', fontSize: '10px', fontWeight: 800, letterSpacing: '1px', textTransform: 'uppercase' }}>Today's Challenge</div>
                  <div style={{ color: '#f8fafc', fontSize: '15px', fontWeight: 600, marginTop: '2px' }}>5-Minute Core Activation</div>
                </div>
              </div>
            </div>

            <button style={{ border: 'none', background: 'linear-gradient(90deg, #e11d48, #be123c)', color: 'var(--app-text)', borderRadius: '12px', padding: '12px', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 14px rgba(225, 29, 72, 0.3)' }}>
              Start 5-Min Timer
            </button>
          </article>

          <article style={{ ...ideaCard, border: '1px solid var(--app-border)' }}>
            <h3 style={{ margin: 0, color: 'var(--app-text)' }}>27) Weekly Momentum</h3>
            <p style={{ margin: 0, color: 'var(--app-text-muted)', fontSize: '13px' }}>Focuses on the bigger picture and maintaining weekly volume.</p>
            
            <div style={{ margin: 'auto 0', display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', height: '60px', padding: '0 8px' }}>
              {[30, 45, 60, 20, 80, 50, 0].map((val, i) => {
                const isToday = i === 5;
                return (
                  <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                    <div style={{ 
                      width: '14px', 
                      height: `${Math.max(val, 4)}px`, 
                      background: isToday ? '#a855f7' : val > 0 ? '#52525b' : '#27272a',
                      borderRadius: '4px',
                      opacity: isToday ? 1 : 0.6
                    }} />
                    <div style={{ fontSize: '9px', color: isToday ? '#c084fc' : '#71717a', fontWeight: isToday ? 800 : 400 }}>
                      {['M','T','W','T','F','S','S'][i]}
                    </div>
                  </div>
                )
              })}
            </div>

            <button style={{ border: '1px solid #a855f7', background: 'rgba(168, 85, 247, 0.1)', color: '#d8b4fe', borderRadius: '12px', padding: '12px', fontWeight: 700, cursor: 'pointer' }}>
              Add to Today's Volume
            </button>
          </article>

          <article
            style={{
              ...ideaCard,
              background: 'linear-gradient(165deg, rgba(17,24,39,0.96) 0%, rgba(24,24,27,0.96) 100%)',
              border: '1px solid rgba(148,163,184,0.28)',
              boxShadow: '0 18px 40px -24px rgba(2,6,23,0.9)'
            }}
          >
            <h3 style={{ margin: 0, color: '#f8fafc' }}>28) Premium Clean (Production Candidate)</h3>
            <p style={{ margin: 0, color: '#94a3b8', fontSize: '13px' }}>
              Quiet premium style tuned to match the dashboard without flashy effects.
            </p>

            <div
              style={{
                marginTop: '8px',
                border: '1px solid rgba(148,163,184,0.24)',
                background: 'rgba(15,23,42,0.58)',
                borderRadius: '14px',
                padding: '14px',
                display: 'grid',
                gap: '8px'
              }}
            >
              <div
                style={{
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.9px',
                  color: '#93c5fd',
                  fontWeight: 700
                }}
              >
                {premiumCleanCard.eyebrow}
              </div>
              <div style={{ fontSize: '24px', lineHeight: 1.15, letterSpacing: '-0.4px', color: '#f8fafc', fontWeight: 700 }}>
                {premiumCleanCard.headline}
              </div>
              <div style={{ fontSize: '13px', lineHeight: 1.55, color: '#cbd5e1' }}>{premiumCleanCard.body}</div>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '7px' }}>
              {premiumCleanCard.chips.map((chip) => (
                <span
                  key={chip}
                  style={{
                    borderRadius: '999px',
                    border: '1px solid rgba(148,163,184,0.24)',
                    background: 'rgba(148,163,184,0.09)',
                    color: '#cbd5e1',
                    fontSize: '11px',
                    padding: '5px 9px'
                  }}
                >
                  {chip}
                </span>
              ))}
            </div>

            <div style={{ marginTop: 'auto', display: 'grid', gridTemplateColumns: '1fr auto', gap: '8px' }}>
              <button
                style={{
                  border: 'none',
                  borderRadius: '11px',
                  background: '#2563eb',
                  color: 'var(--app-text)',
                  fontWeight: 700,
                  padding: '11px',
                  cursor: 'pointer'
                }}
              >
                {premiumCleanCard.primaryCta}
              </button>
              <button
                style={{
                  border: '1px solid rgba(148,163,184,0.3)',
                  borderRadius: '11px',
                  background: 'transparent',
                  color: '#cbd5e1',
                  fontWeight: 600,
                  padding: '11px',
                  cursor: 'pointer'
                }}
              >
                {premiumCleanCard.secondaryCta}
              </button>
            </div>
          </article>

          <article style={{ ...ideaCard, border: '1px solid rgba(71,85,105,0.42)', background: 'rgba(10,14,23,0.94)' }}>
            <h3 style={{ margin: 0, color: '#f8fafc' }}>29) Replace Start Workout - Clean Feature Set</h3>
            <p style={{ margin: 0, color: '#94a3b8', fontSize: '13px' }}>
              Alternatives that fit the current dashboard style while feeling premium.
            </p>

            <div style={{ marginTop: '8px', display: 'grid', gap: '8px' }}>
              {startActionAlternatives.map((item) => {
                const active = item.id === recommendedAlternativeId;
                return (
                  <div
                    key={item.id}
                    style={{
                      border: active ? '1px solid rgba(37,99,235,0.55)' : '1px solid rgba(71,85,105,0.36)',
                      borderRadius: '12px',
                      background: active ? 'rgba(37,99,235,0.12)' : 'rgba(15,23,42,0.45)',
                      padding: '10px 11px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '8px', alignItems: 'center' }}>
                      <div style={{ fontSize: '13px', fontWeight: 700, color: active ? '#dbeafe' : '#e2e8f0' }}>{item.title}</div>
                      {active ? (
                        <span style={{ fontSize: '10px', color: '#bfdbfe', border: '1px solid rgba(191,219,254,0.5)', borderRadius: '999px', padding: '3px 7px' }}>
                          Recommended now
                        </span>
                      ) : null}
                    </div>
                    <div style={{ marginTop: '4px', fontSize: '12px', color: '#cbd5e1' }}>{item.description}</div>
                    <div style={{ marginTop: '3px', fontSize: '11px', color: '#94a3b8' }}>{item.fit}</div>
                  </div>
                );
              })}
            </div>

            <button
              style={{
                marginTop: 'auto',
                border: 'none',
                borderRadius: '12px',
                background: '#1d4ed8',
                color: 'var(--app-text)',
                fontWeight: 700,
                padding: '11px',
                cursor: 'pointer'
              }}
            >
              Use recommended feature
            </button>
          </article>

          <article style={{ ...ideaCard, border: '1px solid rgba(99,102,241,0.36)' }}>
            <h3 style={{ margin: 0, color: '#f8fafc' }}>30) Neon Ring CTA Mix (8 + 12)</h3>
            <p style={{ margin: 0, color: '#cbd5e1', fontSize: '13px' }}>
              Centered neon rings with a clean, clear action button.
            </p>

            <div style={{ flex: 1, display: 'grid', placeItems: 'center', marginTop: '8px' }}>
              <div
                className="ring-glow"
                style={{
                  width: '148px',
                  height: '148px',
                  borderRadius: '50%',
                  background: `conic-gradient(#4f46e5 ${ringMetrics.workout}%, var(--app-border) ${ringMetrics.workout}% 100%)`,
                  display: 'grid',
                  placeItems: 'center',
                  boxShadow: '0 0 20px rgba(79,70,229,0.28)'
                }}
              >
                <div
                  style={{
                    width: '112px',
                    height: '112px',
                    borderRadius: '50%',
                    background: `conic-gradient(#06b6d4 ${ringMetrics.sleep}%, var(--app-border) ${ringMetrics.sleep}% 100%)`,
                    display: 'grid',
                    placeItems: 'center',
                    boxShadow: '0 0 18px rgba(6,182,212,0.25)'
                  }}
                >
                  <div
                    style={{
                      width: '80px',
                      height: '80px',
                      borderRadius: '50%',
                      background: `conic-gradient(#ec4899 ${ringMetrics.nutrition}%, var(--app-border) ${ringMetrics.nutrition}% 100%)`,
                      display: 'grid',
                      placeItems: 'center',
                      boxShadow: '0 0 18px rgba(236,72,153,0.24)'
                    }}
                  >
                    <div
                      style={{
                        width: '56px',
                        height: '56px',
                        borderRadius: '50%',
                        background: '#0f172a',
                        border: '1px solid rgba(236,72,153,0.4)',
                        display: 'grid',
                        placeItems: 'center',
                        textAlign: 'center'
                      }}
                    >
                      <div style={{ fontSize: '15px', lineHeight: 1 }}>{meta.icon}</div>
                      <div style={{ fontSize: '11px', color: '#fce7f3', fontWeight: 800 }}>{score}%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', alignItems: 'center' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#4f46e5', boxShadow: '0 0 10px rgba(79,70,229,0.9)' }} />
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#06b6d4', boxShadow: '0 0 10px rgba(6,182,212,0.9)' }} />
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ec4899', boxShadow: '0 0 10px rgba(236,72,153,0.9)' }} />
            </div>

            <button
              style={{
                marginTop: 'auto',
                alignSelf: 'center',
                minWidth: '190px',
                border: `2px solid ${status === 'meal' ? '#ec4899' : status === 'done' ? '#22c55e' : status === 'sync' ? '#06b6d4' : '#4f46e5'}`,
                borderRadius: '999px',
                background: status === 'meal' ? 'rgba(236,72,153,0.17)' : status === 'done' ? 'rgba(34,197,94,0.17)' : status === 'sync' ? 'rgba(6,182,212,0.14)' : 'rgba(79,70,229,0.2)',
                color: 'var(--app-text)',
                fontWeight: 800,
                letterSpacing: '0.4px',
                padding: '11px 16px',
                cursor: 'pointer',
                boxShadow: status === 'meal' ? '0 0 14px rgba(236,72,153,0.32)' : status === 'done' ? '0 0 14px rgba(34,197,94,0.3)' : status === 'sync' ? '0 0 14px rgba(6,182,212,0.28)' : '0 0 14px rgba(79,70,229,0.32)'
              }}
            >
              {meta.icon} {meta.title}
            </button>
          </article>

          <article
            style={{
              ...ideaCard,
              border: '1px solid rgba(96,165,250,0.3)',
              background: 'linear-gradient(160deg, rgba(10,18,32,0.94) 0%, rgba(17,24,39,0.96) 100%)'
            }}
          >
            <h3 style={{ margin: 0, color: '#f8fafc' }}>31) Orbit Fusion Clear (Clean Mix)</h3>
            <p style={{ margin: 0, color: '#9fb2cb', fontSize: '13px' }}>
              Cleaner version of Idea 8 + 12 with muted premium tones and minimal glow.
            </p>

            <div style={{ flex: 1, display: 'grid', placeItems: 'center', marginTop: '8px' }}>
              <div
                style={{
                  width: '172px',
                  height: '172px',
                  borderRadius: '50%',
                  background: `conic-gradient(#0ea5e9 ${ringMetrics.sleep}%, var(--app-border) ${ringMetrics.sleep}% 100%)`,
                  border: '1px solid rgba(56,189,248,0.24)',
                  display: 'grid',
                  placeItems: 'center',
                  boxShadow: '0 0 16px rgba(14,165,233,0.15)'
                }}
              >
                <div
                  style={{
                    width: '132px',
                    height: '132px',
                    borderRadius: '50%',
                    background: `conic-gradient(#4f46e5 ${ringMetrics.workout}%, var(--app-border) ${ringMetrics.workout}% 100%)`,
                    border: '1px solid rgba(129,140,248,0.24)',
                    display: 'grid',
                    placeItems: 'center'
                  }}
                >
                  <div
                    style={{
                      width: '94px',
                      height: '94px',
                      borderRadius: '50%',
                      background: `conic-gradient(#14b8a6 ${ringMetrics.nutrition}%, var(--app-border) ${ringMetrics.nutrition}% 100%)`,
                      border: '1px solid rgba(45,212,191,0.24)',
                      display: 'grid',
                      placeItems: 'center'
                    }}
                  >
                    <div
                      style={{
                        width: '68px',
                        height: '68px',
                        borderRadius: '50%',
                        background: '#0b1220',
                        border: '1px solid rgba(148,163,184,0.3)',
                        display: 'grid',
                        placeItems: 'center',
                        textAlign: 'center'
                      }}
                    >
                      <div style={{ fontSize: '16px', lineHeight: 1 }}>{meta.icon}</div>
                      <div style={{ fontSize: '12px', color: '#dbeafe', fontWeight: 700 }}>{score}%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
              <div style={{ border: '1px solid rgba(129,140,248,0.4)', borderRadius: '9px', padding: '6px 8px', background: 'rgba(79,70,229,0.14)' }}>
                <div style={{ fontSize: '10px', color: '#c7d2fe', textTransform: 'uppercase' }}>Workout</div>
                <div style={{ fontSize: '13px', color: '#e2e8f0', fontWeight: 700 }}>{ringMetrics.workout}%</div>
              </div>
              <div style={{ border: '1px solid rgba(56,189,248,0.4)', borderRadius: '9px', padding: '6px 8px', background: 'rgba(14,165,233,0.14)' }}>
                <div style={{ fontSize: '10px', color: '#bae6fd', textTransform: 'uppercase' }}>Sleep</div>
                <div style={{ fontSize: '13px', color: '#e2e8f0', fontWeight: 700 }}>{ringMetrics.sleep}%</div>
              </div>
              <div style={{ border: '1px solid rgba(45,212,191,0.4)', borderRadius: '9px', padding: '6px 8px', background: 'rgba(20,184,166,0.14)' }}>
                <div style={{ fontSize: '10px', color: '#99f6e4', textTransform: 'uppercase' }}>Nutrition</div>
                <div style={{ fontSize: '13px', color: '#e2e8f0', fontWeight: 700 }}>{ringMetrics.nutrition}%</div>
              </div>
            </div>

            <button
              style={{
                marginTop: 'auto',
                border: '1px solid rgba(96,165,250,0.45)',
                borderRadius: '11px',
                background: '#1e3a8a',
                color: '#eff6ff',
                fontWeight: 700,
                padding: '11px',
                cursor: 'pointer'
              }}
            >
              {meta.title} - Clear Mix
            </button>
          </article>

          <article
            style={{
              ...ideaCard,
              background: 'rgba(15,23,42,0.38)',
              backdropFilter: 'blur(14px)',
              border: '1px solid rgba(148,163,184,0.26)'
            }}
          >
            <h3 style={{ margin: 0, color: '#f8fafc' }}>32) Glass Slide Neo (Simple Mix)</h3>
            <p style={{ margin: 0, color: '#94a3b8', fontSize: '13px' }}>
              Mix of Idea 7, 21, and 23 with a minimal, easy-to-read layout.
            </p>

            <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div
                style={{
                  width: '62px',
                  height: '62px',
                  borderRadius: '16px',
                  background: 'linear-gradient(135deg, #2b2f3a 0%, #171a22 100%)',
                  border: '1px solid var(--app-border)',
                  display: 'grid',
                  placeItems: 'center',
                  fontSize: '28px',
                  boxShadow: 'inset 1px 1px 0 var(--app-border), 6px 8px 18px rgba(0,0,0,0.35)'
                }}
              >
                {meta.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '16px', fontWeight: 800, color: '#f8fafc' }}>{meta.title}</div>
                <div style={{ marginTop: '3px', fontSize: '12px', color: '#cbd5e1' }}>Tap or slide to confirm action</div>
              </div>
            </div>

            <div
              style={{
                marginTop: '10px',
                background: 'rgba(15,23,42,0.72)',
                border: '1px solid rgba(148,163,184,0.26)',
                borderRadius: '999px',
                padding: '5px',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #4f46e5, #06b6d4)',
                  display: 'grid',
                  placeItems: 'center',
                  color: 'var(--app-text)',
                  fontWeight: 800,
                  boxShadow: '0 6px 14px rgba(79,70,229,0.45)'
                }}
              >
                »
              </div>
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  display: 'grid',
                  placeItems: 'center',
                  fontSize: '12px',
                  color: '#cbd5e1',
                  fontWeight: 700,
                  letterSpacing: '0.6px',
                  pointerEvents: 'none'
                }}
              >
                Slide to Start
              </div>
            </div>

            <button
              style={{
                marginTop: 'auto',
                border: '1px solid rgba(129,140,248,0.45)',
                borderRadius: '11px',
                background: 'rgba(79,70,229,0.2)',
                color: '#eef2ff',
                fontWeight: 700,
                padding: '11px',
                cursor: 'pointer'
              }}
            >
            </button>
          </article>

          <article style={{ ...ideaCard, gridColumn: '1 / -1', padding: 0, overflow: 'hidden', background: 'var(--app-bg)', border: '1px solid var(--app-border)' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--app-border)', background: 'linear-gradient(90deg, rgba(79,70,229,0.1), transparent)' }}>
              <h3 style={{ margin: 0, color: '#f8fafc', fontSize: '18px' }}>33) Universal Adaptive Layout (Desktop + Mobile)</h3>
              <p style={{ margin: '4px 0 0', color: '#94a3b8', fontSize: '14px', lineHeight: 1.5 }}>
                Scales perfectly from an immersive desktop dashboard widget to a sticky, highly-accessible bottom command bar on mobile screens. 
                <span style={{color: '#a5b4fc', fontWeight: 600}}> Resize your browser window below 768px to see it snap to mobile view!</span>
              </p>
            </div>
            {/* The responsive container */}
            <div className="adaptive-hero-container">
              {/* Desktop/Tablet View */}
              <div className="adaptive-desktop-view">
                <div style={{ display: 'flex', gap: '24px', alignItems: 'center', flex: 1 }}>
                  <div style={{
                    width: '90px', height: '90px', borderRadius: '50%', background: 'conic-gradient(from 0deg, #6366f1, #ec4899, #6366f1)',
                    display: 'grid', placeItems: 'center', boxShadow: '0 0 25px rgba(99, 102, 241, 0.3)'
                  }}>
                    <div style={{ width: '82px', height: '82px', borderRadius: '50%', background: 'var(--app-surface)', display: 'grid', placeItems: 'center', fontSize: '36px' }}>
                      {meta.icon}
                    </div>
                  </div>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ fontSize: '12px', color: '#818cf8', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '1.5px' }}>Current Mission</div>
                      <div style={{ fontSize: '11px', background: 'rgba(99,102,241,0.2)', color: '#c7d2fe', padding: '2px 8px', borderRadius: '4px', fontWeight: 700 }}>
                        {score}% Setup
                      </div>
                    </div>
                    <div style={{ fontSize: '32px', fontWeight: 900, color: 'var(--app-text)', margin: '4px 0', letterSpacing: '-0.5px' }}>{meta.title}</div>
                    <div style={{ fontSize: '15px', color: 'var(--app-text-muted)' }}>{meta.subtitle}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', minWidth: '220px' }}>
                  <button style={{ background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', border: 'none', padding: '16px', borderRadius: '14px', color: 'var(--app-text)', fontWeight: 800, fontSize: '16px', cursor: 'pointer', boxShadow: '0 4px 20px rgba(79, 70, 229, 0.4)', transition: 'transform 0.2s', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    Start {meta.label} <span>→</span>
                  </button>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button style={{ flex: 1, background: 'var(--app-border)', border: '1px solid var(--app-border)', padding: '12px', borderRadius: '10px', color: '#e2e8f0', cursor: 'pointer', fontSize: '13px', fontWeight: 600 }}>💧 Water</button>
                    <button style={{ flex: 1, background: 'var(--app-border)', border: '1px solid var(--app-border)', padding: '12px', borderRadius: '10px', color: '#e2e8f0', cursor: 'pointer', fontSize: '13px', fontWeight: 600 }}>😴 Sleep</button>
                  </div>
                </div>
              </div>

              {/* Mobile View (Simulated Sticky Command Bar) */}
              <div className="adaptive-mobile-view">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                  <div>
                    <div style={{ fontSize: '11px', color: 'var(--app-text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px' }}>Next Up</div>
                    <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--app-text)' }}>{meta.title}</div>
                  </div>
                  <div style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(236,72,153,0.1))', border: '1px solid rgba(99,102,241,0.3)', color: '#c7d2fe', padding: '4px 10px', borderRadius: '8px', fontSize: '13px', fontWeight: 700 }}>
                    Day: {score}%
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto auto', gap: '10px' }}>
                  <button style={{ background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', border: 'none', padding: '14px', borderRadius: '12px', color: 'var(--app-text)', fontWeight: 800, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', fontSize: '15px' }}>
                    <span style={{fontSize: '20px'}}>{meta.icon}</span> Start {meta.label}
                  </button>
                  <button style={{ background: 'var(--app-border)', border: '1px solid var(--app-border)', width: '50px', height: '50px', borderRadius: '12px', display: 'grid', placeItems: 'center', fontSize: '22px' }}>💧</button>
                  <button style={{ background: 'var(--app-border)', border: '1px solid var(--app-border)', width: '50px', height: '50px', borderRadius: '12px', display: 'grid', placeItems: 'center', fontSize: '22px' }}>😴</button>
                </div>
              </div>
            </div>
          </article>

        </section>
      </main>
    </div>
  );
}

export default DashboardActionIdeas;
