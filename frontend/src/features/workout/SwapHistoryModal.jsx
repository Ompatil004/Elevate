import React from 'react';
import { styles } from './workoutStyles';
import { weekdayNames, formatSwapTimestamp } from './workoutConstants';

export default function SwapHistoryModal({
  show,
  onClose,
  historyTab,
  setHistoryTab,
  swapLimits,
  swapHistory,
  pastWorkouts,
  selectedHistory,
  setSelectedHistory,
  workoutLayout,
}) {
  if (!show) return null;

  return (
    <div style={workoutLayout?.historyPanel || styles.historyPanel}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div style={{ fontSize: '20px', fontWeight: '800', color: 'var(--app-text)' }}>History</div>
        <button
          onClick={onClose}
          style={{ background: 'none', border: 'none', color: 'var(--app-text)', fontSize: '20px', cursor: 'pointer' }}
        >
          ✕
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '16px' }}>
        <button
          onClick={() => setHistoryTab('workout')}
          style={{
            padding: '10px 12px',
            borderRadius: '10px',
            border: historyTab === 'workout' ? '1px solid #6366f1' : '1px solid var(--app-border)',
            background: historyTab === 'workout' ? 'rgba(99,102,241,0.18)' : 'var(--quote-bg)',
            color: 'var(--app-text)',
            fontWeight: '700',
            cursor: 'pointer',
          }}
        >
          Workouts
        </button>
        <button
          onClick={() => setHistoryTab('swap')}
          style={{
            padding: '10px 12px',
            borderRadius: '10px',
            border: historyTab === 'swap' ? '1px solid #f59e0b' : '1px solid var(--app-border)',
            background: historyTab === 'swap' ? 'rgba(245,158,11,0.15)' : 'var(--quote-bg)',
            color: 'var(--app-text)',
            fontWeight: '700',
            cursor: 'pointer',
          }}
        >
          Swaps ({swapLimits.used}/{swapLimits.max})
        </button>
      </div>

      {historyTab === 'workout' ? (
        <>
          {pastWorkouts && pastWorkouts.length > 0 ? (
            pastWorkouts.map((day, i) => (
              <div
                key={i}
                style={styles.historyItem}
                className="history-card"
                onClick={() => setSelectedHistory(selectedHistory === i ? null : i)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={styles.historyDate}>{day.date || new Date().toLocaleDateString()}</div>
                  <div style={{ fontSize: '12px', fontWeight: '700', color: day.status === 'Completed' ? '#22c55e' : '#ef4444' }}>
                    {day.status || 'Completed'}
                  </div>
                </div>
                {selectedHistory === i && day.details && (
                  <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px solid var(--app-border)' }}>
                    <div style={styles.historyLabel}>Details:</div>
                    <div style={styles.historyList}>
                      <div style={{ marginBottom: '4px' }}>{day.details}</div>
                    </div>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#52525b' }}>No workout history yet</div>
          )}
        </>
      ) : (
        <>
          <div
            style={{
              background: 'rgba(245, 158, 11, 0.08)',
              border: '1px solid rgba(245, 158, 11, 0.28)',
              borderRadius: '12px',
              padding: '12px',
              marginBottom: '14px',
            }}
          >
            <div style={{ fontSize: '12px', color: '#fbbf24', fontWeight: '700', marginBottom: '4px' }}>
              Weekly Swap Limits
            </div>
            <div style={{ fontSize: '13px', color: 'var(--app-text)' }}>
              Used: {swapLimits.used} / {swapLimits.max}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--app-text-muted)', marginTop: '2px' }}>
              Remaining this week: {Math.max(0, swapLimits.remaining)}
            </div>
          </div>

          {swapHistory.length > 0 ? (
            swapHistory
              .slice()
              .reverse()
              .map((entry, idx) => {
                const fromIdx = Number(entry?.from_day);
                const toIdx = Number(entry?.to_day);
                const fromLabel = Number.isInteger(fromIdx) && fromIdx >= 0 && fromIdx <= 6 ? weekdayNames[fromIdx] : `Day ${fromIdx + 1}`;
                const toLabel = Number.isInteger(toIdx) && toIdx >= 0 && toIdx <= 6 ? weekdayNames[toIdx] : `Day ${toIdx + 1}`;
                const isRestToWorkout = entry?.direction === 'rest_to_workout';

                return (
                  <div key={`swap-history-${idx}`} style={styles.historyItem} className="history-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <div style={{ ...styles.historyDate, marginBottom: 0 }}>
                        {isRestToWorkout ? 'Rest -> Workout' : 'Workout -> Rest'}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--app-text-muted)' }}>
                        {formatSwapTimestamp(entry?.timestamp)}
                      </div>
                    </div>
                    <div style={{ fontSize: '13px', color: 'var(--app-text)', marginBottom: '6px' }}>
                      {`${fromLabel} -> ${toLabel}`}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--app-text-muted)' }}>
                      Focus: {entry?.workout_focus || 'Workout'}
                    </div>
                  </div>
                );
              })
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#52525b' }}>No swaps recorded this week</div>
          )}
        </>
      )}
    </div>
  );
}
