import React from 'react';

export default function ExerciseVariationModal({
  variationResult,
  onDismiss,
}) {
  if (!variationResult) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(15, 23, 42, 0.85)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 9999,
        animation: 'fadeIn 0.3s ease-out',
      }}
    >
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(30, 27, 75, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.35)',
          boxShadow: '0 24px 64px rgba(0, 0, 0, 0.5), 0 0 40px rgba(99, 102, 241, 0.15)',
          borderRadius: '24px',
          width: '90%',
          maxWidth: '520px',
          padding: '30px',
          position: 'relative',
          color: 'var(--app-text)',
          textAlign: 'center',
          animation: 'slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        }}
      >
        {variationResult.loading ? (
          <div style={{ padding: '40px 0' }}>
            <div
              style={{
                width: '60px',
                height: '60px',
                border: '4px solid rgba(99, 102, 241, 0.1)',
                borderTop: '4px solid #6366f1',
                borderRadius: '50%',
                margin: '0 auto 20px',
                animation: 'spin 1s linear infinite',
              }}
            />
            <h3 style={{ fontSize: '20px', fontWeight: '800', marginBottom: '8px' }}>SESSION COMPLETE!</h3>
            <p style={{ color: 'var(--app-text-muted)', fontSize: '14px' }}>
              Analysing form and preparing progression suggestions...
            </p>
          </div>
        ) : (
          <>
            <div style={{ fontSize: '50px', marginBottom: '15px' }}>
              {variationResult.suggestion?.action === 'progress'
                ? '🚀'
                : variationResult.suggestion?.action === 'regress'
                ? '🔄'
                : '🎉'}
            </div>

            <h2
              style={{
                fontSize: '24px',
                fontWeight: '800',
                marginBottom: '4px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
              }}
            >
              {variationResult.suggestion?.action === 'progress'
                ? 'Progression Unlocked!'
                : variationResult.suggestion?.action === 'regress'
                ? 'Form Correction Recommended'
                : 'Workout Complete!'}
            </h2>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                background: 'rgba(99, 102, 241, 0.15)',
                padding: '4px 12px',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: '700',
                color: '#a5b4fc',
                marginBottom: '24px',
              }}
            >
              <span>AI COACH RATING</span> • <span>SCORE: {Math.round((variationResult.formScore || 0) * 100)}%</span>
            </div>

            <div
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: '16px',
                padding: '18px',
                marginBottom: '24px',
                textAlign: 'left',
              }}
            >
              <div
                style={{
                  fontSize: '11px',
                  fontWeight: '800',
                  color: 'var(--app-text-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                  marginBottom: '8px',
                }}
              >
                Recommendation for {variationResult.exercise}
              </div>
              {variationResult.suggestion?.suggested_exercise && (
                <div style={{ fontSize: '16px', fontWeight: '700', color: 'var(--app-text)', marginBottom: '8px' }}>
                  {variationResult.suggestion.action === 'progress'
                    ? 'Try next: '
                    : variationResult.suggestion.action === 'regress'
                    ? 'Easier swap: '
                    : 'Keep variation: '}
                  <span style={{ color: '#22d3ee' }}>{variationResult.suggestion.suggested_exercise}</span>
                </div>
              )}
              {variationResult.coaching?.primary_message ? (
                <p style={{ fontSize: '13px', color: 'var(--app-text-muted)', margin: 0, lineHeight: '1.5' }}>
                  {variationResult.coaching.primary_message}
                </p>
              ) : variationResult.suggestion?.reason ? (
                <p style={{ fontSize: '13px', color: 'var(--app-text-muted)', margin: 0, lineHeight: '1.5' }}>
                  {variationResult.suggestion.reason}
                </p>
              ) : null}
            </div>

            <button
              onClick={() => onDismiss(variationResult)}
              style={{
                background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                padding: '14px 28px',
                fontWeight: '800',
                fontSize: '15px',
                width: '100%',
                cursor: 'pointer',
                boxShadow: '0 8px 20px rgba(99, 102, 241, 0.3)',
                transition: 'all 0.2s',
              }}
            >
              SAVE & EXIT WORKOUT
            </button>
          </>
        )}
      </div>
    </div>
  );
}
