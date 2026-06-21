import React, { useState, useEffect, useCallback } from 'react';

const formatClock = (seconds) => {
  const safeSeconds = Math.max(0, Number(seconds) || 0);
  const mins = Math.floor(safeSeconds / 60);
  const secs = safeSeconds % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
};

const TimerExerciseMode = ({
  onComplete,
  onSkip,
  targetSets = 1,
  targetDuration = 300,
  restDuration = 60,
}) => {
  const normalizedTargetSets = Math.max(1, Number(targetSets) || 1);
  const normalizedTargetDuration = Math.max(1, Number(targetDuration) || 300);
  const normalizedRestDuration = Math.max(0, Number(restDuration) || 60);

  const [currentSet, setCurrentSet] = useState(1);
  const [timeLeft, setTimeLeft] = useState(normalizedTargetDuration);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isResting, setIsResting] = useState(false);
  const [restTimeLeft, setRestTimeLeft] = useState(normalizedRestDuration);

  const handleSetComplete = useCallback(() => {
    if (currentSet >= normalizedTargetSets) {
      if (typeof onComplete === 'function') {
        onComplete();
      }
      return;
    }

    setIsRunning(false);
    setIsPaused(false);
    setIsResting(true);
    setRestTimeLeft(normalizedRestDuration);
  }, [currentSet, normalizedTargetSets, normalizedRestDuration, onComplete]);

  useEffect(() => {
    if (!isRunning || isPaused || isResting) return undefined;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          setTimeout(() => {
            handleSetComplete();
          }, 0);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isRunning, isPaused, isResting, handleSetComplete]);

  useEffect(() => {
    if (!isResting) return undefined;

    const timer = setInterval(() => {
      setRestTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          setTimeout(() => {
            setIsResting(false);
            setCurrentSet((current) => current + 1);
            setTimeLeft(normalizedTargetDuration);
            setIsRunning(true);
            setIsPaused(false);
          }, 0);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isResting, normalizedTargetDuration]);

  const handleToggle = () => {
    if (!isRunning) {
      setIsRunning(true);
      setIsPaused(false);
      return;
    }
    setIsPaused((prev) => !prev);
  };

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(145deg, #0f0f14 0%, #1a1a24 100%)',
        zIndex: 20,
        padding: '24px',
      }}
    >
      {isResting ? (
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', color: '#f59e0b', marginBottom: '20px', fontWeight: '800' }}>
            REST TIME
          </div>
          <div style={{ fontSize: '96px', fontWeight: '900', color: '#f59e0b', lineHeight: 1 }}>
            {formatClock(restTimeLeft)}
          </div>
          <button
            type="button"
            onClick={() => setRestTimeLeft(0)}
            style={{
              marginTop: '30px',
              padding: '12px 24px',
              background: '#3f3f46',
              border: 'none',
              color: 'white',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '700',
            }}
          >
            Skip Rest
          </button>
        </div>
      ) : (
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '18px', color: '#a1a1aa', marginBottom: '10px' }}>
            SET {currentSet} OF {normalizedTargetSets}
          </div>
          <div
            style={{
              fontSize: '108px',
              fontWeight: '900',
              color: isRunning && !isPaused ? '#22c55e' : '#6366f1',
              lineHeight: 1,
            }}
          >
            {formatClock(timeLeft)}
          </div>

          <div style={{ display: 'flex', gap: '20px', marginTop: '40px', justifyContent: 'center' }}>
            <button
              type="button"
              onClick={handleToggle}
              style={{
                padding: '16px 48px',
                fontSize: '18px',
                fontWeight: '700',
                background: !isRunning ? '#6366f1' : isPaused ? '#22c55e' : '#f59e0b',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                cursor: 'pointer',
                minWidth: '170px',
              }}
            >
              {!isRunning ? 'START' : isPaused ? 'RESUME' : 'PAUSE'}
            </button>
            <button
              type="button"
              onClick={() => {
                if (typeof onSkip === 'function') {
                  onSkip();
                }
              }}
              style={{
                padding: '16px 48px',
                fontSize: '18px',
                fontWeight: '700',
                background: 'transparent',
                color: '#ef4444',
                border: '2px solid #ef4444',
                borderRadius: '12px',
                cursor: 'pointer',
              }}
            >
              SKIP
            </button>
          </div>
          <div style={{ marginTop: '30px', color: '#71717a', fontSize: '14px' }}>
            Camera is not required for this exercise
          </div>
        </div>
      )}
    </div>
  );
};

export default TimerExerciseMode;
