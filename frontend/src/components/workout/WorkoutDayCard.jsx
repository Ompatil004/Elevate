/**
 * WorkoutDayCard.jsx
 *
 * BUG-F2/F8: Extracted from Workout.jsx (lines 1978–2111).
 * Renders a single day card in the weekly workout grid.
 * Pure presentational component — no API calls.
 *
 * Props:
 *   day             – plan day object from Python backend
 *   dayIdx          – 0-6 (Mon-Sun)
 *   status          – 'TODAY' | 'COMPLETED' | 'PAST' | 'NOT_STARTED' | 'REST' | 'NO PLAN' | 'UPCOMING'
 *   isRest          – boolean
 *   isPlaceholder   – boolean
 *   isToday         – boolean
 *   layout          – responsive layout tokens from Workout.jsx
 *   styles          – base styles object from Workout.jsx
 *   weekdayNames    – ['Monday', …, 'Sunday']
 *   onStartWorkout  – (dayIdx: number) => void
 *   onSwapToRest    – (dayIdx: number) => void
 *   canSwapToRest   – boolean
 */

import React from 'react';

// Status → badge colours (avoids recomputing inline)
const STATUS_BG = {
  TODAY:       'rgba(99, 102, 241, 0.2)',
  COMPLETED:   'rgba(34, 197, 94, 0.2)',
  NOT_STARTED: 'rgba(113, 113, 122, 0.2)',
  PAST:        'rgba(239, 68, 68, 0.2)',
  REST:        'rgba(245, 158, 11, 0.2)',
  'NO PLAN':   'rgba(113, 113, 122, 0.2)',
};
const STATUS_COLOR = {
  TODAY:       '#a5b4fc',
  COMPLETED:   '#22c55e',
  NOT_STARTED: '#a1a1aa',
  PAST:        '#ef4444',
  REST:        '#f59e0b',
  'NO PLAN':   '#a1a1aa',
};
const STATUS_BORDER = {
  TODAY:       'rgba(99, 102, 241, 0.3)',
  COMPLETED:   'rgba(34, 197, 94, 0.3)',
  NOT_STARTED: 'rgba(113, 113, 122, 0.3)',
  PAST:        'rgba(239, 68, 68, 0.3)',
  REST:        'rgba(245, 158, 11, 0.3)',
  'NO PLAN':   'rgba(113, 113, 122, 0.3)',
};
const DEFAULT_COLOR  = '#a1a1aa';
const DEFAULT_BG     = 'rgba(161, 161, 170, 0.2)';
const DEFAULT_BORDER = 'rgba(161, 161, 170, 0.3)';

const WorkoutDayCard = React.memo(({
  day,
  dayIdx,
  status,
  isRest,
  isPlaceholder,
  isToday,
  layout,
  styles,
  weekdayNames,
  onStartWorkout,
  onSwapToRest,
  canSwapToRest,
}) => {
  const dayExercises   = day.exercises || [];
  const previewExercises = dayExercises.filter((ex) => !ex?.is_warmup);
  const displayExercises = previewExercises.length > 0 ? previewExercises : dayExercises;

  // Card style based on status
  let cardStyle = { ...layout.card };
  if (status === 'TODAY')        cardStyle = { ...cardStyle, ...styles.cardActive };
  else if (status === 'COMPLETED') cardStyle = { ...cardStyle, ...styles.cardDone };
  else if (status === 'NOT_STARTED') cardStyle = {
    ...cardStyle,
    border:     '1px dashed rgba(161, 161, 170, 0.25)',
    background: 'rgba(113, 113, 122, 0.05)',
    opacity:    0.75,
  };
  else if (status === 'PAST')                 cardStyle = { ...cardStyle, ...styles.cardMissed };
  else if (isRest || isPlaceholder)           cardStyle = { ...cardStyle, border: '1px dashed rgba(255,255,255,0.2)', opacity: 0.7 };

  return (
    <div
      style={cardStyle}
      onClick={() => !isPlaceholder && !isRest && onStartWorkout(dayIdx)}
    >
      {/* Header: day name + status badge */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <div>
          <div style={styles.dayTitle}>
            {weekdayNames[dayIdx] || `Day ${dayIdx + 1}`}
          </div>
          <div style={styles.focusText}>
            {day.focus || day.day || 'Workout'}
          </div>
        </div>
        <div style={{
          padding:         '4px 10px',
          borderRadius:    '20px',
          fontSize:        '11px',
          fontWeight:      '700',
          textTransform:   'uppercase',
          background:      STATUS_BG[status]    ?? DEFAULT_BG,
          color:           STATUS_COLOR[status] ?? DEFAULT_COLOR,
          border: `1px solid ${STATUS_BORDER[status] ?? DEFAULT_BORDER}`,
        }}>
          {status}
        </div>
      </div>

      {/* Card body */}
      {isRest ? (
        <div style={layout.restDay}>
          😴 Rest Day - Recovery &amp; Preparation
          <div style={{ marginTop: '12px', fontSize: '11px', opacity: 0.9 }}>
            {isToday
              ? 'Tap this card to choose: keep rest day or borrow next workout.'
              : 'No workout today. Focus on recovery, stretching, or light walking.'}
          </div>
        </div>
      ) : status === 'NOT_STARTED' ? (
        <div style={{
          ...layout.restDay,
          display:        'flex',
          flexDirection:  'column',
          alignItems:     'center',
          justifyContent: 'center',
          gap:            '8px',
          color:          '#a1a1aa',
        }}>
          <div style={{ fontSize: '34px' }}>📅</div>
          <div style={{ fontSize: '14px', fontWeight: '700' }}>Not Started Yet</div>
          <div style={{ fontSize: '12px', opacity: 0.9 }}>No workout completion recorded for this day yet.</div>
        </div>
      ) : isPlaceholder ? (
        <div style={layout.restDay}>
          📅 No plan for this day
          <div style={{ marginTop: '12px', fontSize: '11px', opacity: 0.9 }}>
            Generate a new plan to fill this day.
          </div>
        </div>
      ) : (
        <>
          {/* Exercise preview list */}
          {displayExercises.length > 0 && (
            <div style={{ flex: 1, marginBottom: '12px' }}>
              {displayExercises.slice(0, 3).map((ex, i) => (
                <div key={i} style={styles.exPreview}>
                  <span>• {ex.name}</span>
                  <span>{ex.sets}x{ex.reps}</span>
                </div>
              ))}
              {displayExercises.length > 3 && (
                <div style={{ ...styles.exPreview, color: '#a1a1aa', fontSize: '11px' }}>
                  +{displayExercises.length - 3} more exercises
                </div>
              )}
            </div>
          )}

          {/* Action buttons */}
          {!isPlaceholder && (
            <div style={{ marginTop: 'auto', display: 'grid', gap: '10px' }}>
              {isToday ? (
                <button
                  id={`start-workout-day-${dayIdx}`}
                  onClick={(e) => { e.stopPropagation(); onStartWorkout(dayIdx); }}
                  style={{
                    width:        '100%',
                    padding:      '12px',
                    borderRadius: '12px',
                    border:       'none',
                    background:   '#6366f1',
                    color:        'white',
                    fontWeight:   '700',
                    fontSize:     '14px',
                    cursor:       'pointer',
                  }}
                >
                  START WORKOUT
                </button>
              ) : status !== 'REST' && status !== 'NO PLAN' && (
                <button
                  id={`view-workout-day-${dayIdx}`}
                  onClick={(e) => { e.stopPropagation(); onStartWorkout(dayIdx); }}
                  style={{
                    width:        '100%',
                    padding:      '10px',
                    borderRadius: '10px',
                    border:       '1px solid rgba(99,102,241,0.3)',
                    background:   'rgba(99,102,241,0.08)',
                    color:        '#a5b4fc',
                    fontWeight:   '700',
                    fontSize:     '13px',
                    cursor:       'pointer',
                  }}
                >
                  VIEW EXERCISES
                </button>
              )}
              {isToday && canSwapToRest && (
                <button
                  id={`swap-to-rest-day-${dayIdx}`}
                  onClick={(e) => { e.stopPropagation(); onSwapToRest(dayIdx); }}
                  style={{
                    width:        '100%',
                    padding:      '10px 12px',
                    borderRadius: '10px',
                    border:       '1px solid rgba(245, 158, 11, 0.45)',
                    background:   'rgba(245, 158, 11, 0.12)',
                    color:        '#f59e0b',
                    fontWeight:   '700',
                    fontSize:     '12px',
                    cursor:       'pointer',
                  }}
                >
                  NEED REST TODAY?
                </button>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
});

WorkoutDayCard.displayName = 'WorkoutDayCard';
export default WorkoutDayCard;
