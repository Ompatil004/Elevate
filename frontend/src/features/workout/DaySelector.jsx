import React from 'react';
import { styles } from './workoutStyles';
import {
  weekdayNames,
  getDisplayFocus,
  getMuscleTagStyle,
  isRestDay,
  getDayStatus,
} from './workoutConstants';

export default function DaySelector({
  sortedDisplayPlan,
  toDayIndex,
  todayIdx,
  completedIds,
  handleDayClick,
  canSwapWorkoutToRest,
  openWorkoutToRestModal,
  workoutLayout,
}) {
  return (
    <div style={workoutLayout.grid}>
      {sortedDisplayPlan.map((day, idx) => {
        const dayIdx = toDayIndex(day.day_of_week, idx);
        const isRest = isRestDay(day);
        const isPlaceholder = Boolean(day.is_placeholder);
        const status = getDayStatus(day, todayIdx, completedIds);
        const isToday = status === 'TODAY' || (status === 'REST' && dayIdx === todayIdx);
        const dayExercises = day.exercises || [];
        const previewExercises = dayExercises.filter((ex) => !ex?.is_warmup);
        const displayExercises = previewExercises.length > 0 ? previewExercises : dayExercises;

        let cardStyle = { ...workoutLayout.card };
        if (status === 'TODAY') {
          cardStyle = { ...cardStyle, ...styles.cardActive };
        } else if (status === 'COMPLETED') {
          cardStyle = { ...cardStyle, ...styles.cardDone };
        } else if (status === 'NOT_STARTED') {
          cardStyle = {
            ...cardStyle,
            border: '1px dashed rgba(161, 161, 170, 0.25)',
            background: 'rgba(113, 113, 122, 0.05)',
            opacity: 0.75,
          };
        } else if (status === 'PAST') {
          cardStyle = { ...cardStyle, ...styles.cardMissed };
        } else if (isRest || isPlaceholder) {
          cardStyle = { ...cardStyle, border: '1px dashed rgba(255,255,255,0.2)', opacity: 0.7 };
        }

        return (
          <div
            key={`${dayIdx}-${day.day || idx}`}
            className="plan-card"
            style={cardStyle}
            onClick={() => !isPlaceholder && isToday && handleDayClick(dayIdx)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={styles.dayTitle}>
                  {weekdayNames[dayIdx] || `Day ${idx + 1}`}
                </div>
                <div style={styles.focusText}>
                  {getDisplayFocus(day.focus || day.day || 'Workout')}
                </div>
                {Array.isArray(day.muscle_groups_targeted) && day.muscle_groups_targeted.length > 0 && !isRest && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '6px', marginBottom: '4px' }}>
                    {day.muscle_groups_targeted.map((muscle, mi) => {
                      const tagStyle = getMuscleTagStyle(muscle);
                      return (
                        <span key={mi} style={{
                          padding: '2px 7px',
                          borderRadius: '10px',
                          fontSize: '10px',
                          fontWeight: '700',
                          textTransform: 'uppercase',
                          letterSpacing: '0.4px',
                          background: tagStyle.bg,
                          color: tagStyle.text,
                          border: `1px solid ${tagStyle.border}`,
                          whiteSpace: 'nowrap',
                        }}>
                          {muscle}
                        </span>
                      );
                    })}
                  </div>
                )}
              </div>
              <div style={{
                padding: '4px 10px',
                borderRadius: '20px',
                fontSize: '11px',
                fontWeight: '700',
                textTransform: 'uppercase',
                background: status === 'TODAY' ? 'rgba(99, 102, 241, 0.2)' :
                  status === 'COMPLETED' ? 'rgba(34, 197, 94, 0.2)' :
                    status === 'NOT_STARTED' ? 'rgba(113, 113, 122, 0.2)' :
                      status === 'PAST' ? 'rgba(239, 68, 68, 0.2)' :
                        status === 'REST' ? 'rgba(245, 158, 11, 0.2)' :
                          status === 'NO PLAN' ? 'rgba(113, 113, 122, 0.2)' :
                            'rgba(161, 161, 170, 0.2)',
                color: status === 'TODAY' ? '#a5b4fc' :
                  status === 'COMPLETED' ? '#22c55e' :
                    status === 'NOT_STARTED' ? 'var(--app-text-muted)' :
                      status === 'PAST' ? '#ef4444' :
                        status === 'REST' ? '#f59e0b' :
                          status === 'NO PLAN' ? 'var(--app-text-muted)' :
                            'var(--app-text-muted)',
                border: `1px solid ${status === 'TODAY' ? 'rgba(99, 102, 241, 0.3)' :
                  status === 'COMPLETED' ? 'rgba(34, 197, 94, 0.3)' :
                    status === 'NOT_STARTED' ? 'rgba(113, 113, 122, 0.3)' :
                      status === 'PAST' ? 'rgba(239, 68, 68, 0.3)' :
                        status === 'REST' ? 'rgba(245, 158, 11, 0.3)' :
                          status === 'NO PLAN' ? 'rgba(113, 113, 122, 0.3)' :
                            'rgba(161, 161, 170, 0.3)'}`
              }}>
                {status}
              </div>
            </div>

            {isRest ? (
              <div style={workoutLayout.restDay}>
                😴 Rest Day - Recovery & Preparation
                <div style={{ marginTop: '12px', fontSize: '11px', opacity: 0.9 }}>
                  {isToday ? 'Tap this card to choose: keep rest day or borrow next workout.' : 'No workout today. Focus on recovery, stretching, or light walking.'}
                </div>
              </div>
            ) : status === 'NOT_STARTED' ? (
              <div style={{
                ...workoutLayout.restDay,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                color: 'var(--app-text-muted)',
              }}>
                <div style={{ fontSize: '34px' }}>📅</div>
                <div style={{ fontSize: '14px', fontWeight: '700' }}>Not Started Yet</div>
                <div style={{ fontSize: '12px', opacity: 0.9 }}>Your journey begins today!</div>
              </div>
            ) : isPlaceholder ? (
              <div style={workoutLayout.restDay}>
                📅 No plan for this day
                <div style={{ marginTop: '12px', fontSize: '11px', opacity: 0.9 }}>
                  Generate a new plan to fill this day.
                </div>
              </div>
            ) : (
              <>
                {displayExercises.length > 0 && (
                  <div style={{ flex: 1, marginBottom: '12px' }}>
                    {displayExercises.slice(0, 3).map((ex, i) => (
                      <div key={i} style={styles.exPreview}>
                        <span>• {ex.name}</span>
                        <span>{ex.sets}x{ex.reps}</span>
                      </div>
                    ))}
                    {displayExercises.length > 3 && (
                      <div style={{ ...styles.exPreview, color: 'var(--app-text-muted)', fontSize: '11px' }}>
                        +{displayExercises.length - 3} more exercises
                      </div>
                    )}
                  </div>
                )}
                {isToday && (
                  <div style={{ marginTop: 'auto', display: 'grid', gap: '10px' }}>
                    <button
                      onClick={() => handleDayClick(dayIdx)}
                      style={{
                        width: '100%',
                        padding: '12px',
                        borderRadius: '12px',
                        border: 'none',
                        background: '#6366f1',
                        color: 'white',
                        fontWeight: '700',
                        fontSize: '14px',
                        cursor: 'pointer',
                      }}
                    >
                      START WORKOUT
                    </button>
                    {canSwapWorkoutToRest(dayIdx) && (
                      <button
                        onClick={() => openWorkoutToRestModal(dayIdx)}
                        style={{
                          width: '100%',
                          padding: '10px 12px',
                          borderRadius: '10px',
                          border: '1px solid rgba(245, 158, 11, 0.45)',
                          background: 'rgba(245, 158, 11, 0.12)',
                          color: '#f59e0b',
                          fontWeight: '700',
                          fontSize: '12px',
                          cursor: 'pointer',
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
      })}
    </div>
  );
}
