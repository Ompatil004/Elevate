import { describe, it, expect } from 'vitest';
import { getLegacyFallback, PATTERN_MAP } from '../components/PoseDetector';

describe('PoseDetector Routing & Metadata Propagation', () => {
  const route = (exercise) => {
    return exercise?.movement_pattern
      ? (PATTERN_MAP[exercise.movement_pattern] || 'GENERIC')
      : getLegacyFallback(exercise?.name);
  };

  it('routes Dumbbell Biceps Curl to CURL', () => {
    const ex = { name: 'Dumbbell Biceps Curl', movement_pattern: 'curl' };
    expect(route(ex)).toBe('CURL');
  });

  it('routes Archer Push Up to PRESS', () => {
    const ex = { name: 'Archer Push Up', movement_pattern: 'horizontal_push' };
    expect(route(ex)).toBe('PRESS');
  });

  it('routes Barbell Back Squat to SQUAT', () => {
    const ex = { name: 'Barbell Back Squat', movement_pattern: 'squat' };
    expect(route(ex)).toBe('SQUAT');
  });

  it('routes Pull Up to HINGE (via vertical_pull)', () => {
    const ex = { name: 'Pull Up', movement_pattern: 'vertical_pull' };
    expect(route(ex)).toBe('HINGE');
  });

  it('routes Lateral Raise to RAISE', () => {
    const ex = { name: 'Lateral Raise', movement_pattern: 'lateral_raise' };
    expect(route(ex)).toBe('RAISE');
  });

  it('routes Plank to CORE', () => {
    const ex = { name: 'Plank', movement_pattern: 'plank' };
    expect(route(ex)).toBe('CORE');
  });

  it('routes Unknown Exercise to GENERIC', () => {
    const ex = { name: 'Unknown Exercise', movement_pattern: 'generic' };
    expect(route(ex)).toBe('GENERIC');
  });

  it('falls back to getLegacyFallback when movement_pattern is absent (legacy support)', () => {
    // Legacy client cache/fallback compatibility check
    const legacyEx = { name: 'Bicep Curl' };
    expect(route(legacyEx)).toBe('CURL');
  });
});
