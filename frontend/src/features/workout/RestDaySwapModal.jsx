import React from 'react';
import { weekdayNames, getFutureOriginalRestDays } from './workoutConstants';

export default function RestDaySwapModal({
  show,
  displayPlan,
  swapWorkoutDayIndex,
  todayIdx,
  selectedTargetRestDayIndex,
  setSelectedTargetRestDayIndex,
  onClose,
  onConfirmSwap,
  toDayIndex,
}) {
  if (!show) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        background: 'rgba(0,0,0,0.7)',
        zIndex: 2200,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
      }}
    >
      <div
        style={{
          width: 'min(560px, 96vw)',
          background: 'var(--app-surface)',
          border: '1px solid var(--app-border)',
          borderRadius: '16px',
          padding: '20px',
          boxShadow: '0 25px 50px rgba(0,0,0,0.45)',
        }}
      >
        <div style={{ fontSize: '18px', fontWeight: '800', color: 'var(--app-text)', marginBottom: '8px' }}>
          Move Workout To A Future Rest Day
        </div>
        <div style={{ color: 'var(--app-text-muted)', fontSize: '13px', marginBottom: '16px' }}>
          Pick a future original rest day for this workout. Swapped days are locked and cannot be swapped again.
        </div>

        <div style={{ display: 'grid', gap: '10px', marginBottom: '14px' }}>
          {getFutureOriginalRestDays(displayPlan, swapWorkoutDayIndex, todayIdx).map((day) => {
            const idx = toDayIndex(day?.day_of_week, -1);
            const isSelected = idx === selectedTargetRestDayIndex;
            return (
              <button
                key={`swap-target-${idx}`}
                onClick={() => setSelectedTargetRestDayIndex(idx)}
                style={{
                  textAlign: 'left',
                  padding: '12px 14px',
                  borderRadius: '10px',
                  border: isSelected ? '1px solid #6366f1' : '1px solid var(--app-border)',
                  background: isSelected ? 'rgba(99, 102, 241, 0.18)' : 'var(--quote-bg)',
                  color: 'var(--app-text)',
                  cursor: 'pointer',
                }}
              >
                <div style={{ fontWeight: '700', fontSize: '14px' }}>
                  {weekdayNames[idx] || day?.day || `Day ${idx + 1}`}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--app-text-muted)' }}>Current: Rest Day</div>
              </button>
            );
          })}
        </div>

        <div
          style={{
            fontSize: '12px',
            color: '#f59e0b',
            background: 'rgba(245, 158, 11, 0.1)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '10px',
            padding: '10px 12px',
            marginBottom: '16px',
          }}
        >
          This operation is one-time for both involved days. Use it only when needed.
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <button
            onClick={onClose}
            style={{
              padding: '10px 14px',
              borderRadius: '10px',
              border: '1px solid var(--app-border)',
              background: 'var(--app-surface2)',
              color: 'var(--app-text)',
              cursor: 'pointer',
              fontWeight: '600',
            }}
          >
            Cancel
          </button>
          <button
            onClick={onConfirmSwap}
            disabled={selectedTargetRestDayIndex == null}
            style={{
              padding: '10px 14px',
              borderRadius: '10px',
              border: 'none',
              background: selectedTargetRestDayIndex == null ? 'var(--btn-skip-bg)' : '#6366f1',
              color: selectedTargetRestDayIndex == null ? 'var(--btn-skip-text)' : 'var(--app-text)',
              cursor: selectedTargetRestDayIndex == null ? 'not-allowed' : 'pointer',
              fontWeight: '700',
            }}
          >
            Confirm Move
          </button>
        </div>
      </div>
    </div>
  );
}
