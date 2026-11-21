import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import DaySelector from '../features/workout/DaySelector';

describe('DaySelector Component', () => {
  const mockWorkoutLayout = {
    grid: {},
    card: {},
    restDay: {},
  };

  const samplePlan = [
    {
      day: 'Monday',
      day_of_week: 0,
      type: 'past',
      is_placeholder: true,
      focus: 'Not Started',
      exercises: [],
    },
    {
      day: 'Friday',
      day_of_week: 4,
      type: 'workout',
      is_placeholder: false,
      focus: 'Chest & Triceps',
      muscle_groups_targeted: ['Chest', 'Arms'],
      exercises: [
        { name: 'Barbell Bench Press', sets: 3, reps: '8-12', is_warmup: false },
        { name: 'Incline Dumbbell Press', sets: 3, reps: '10-12', is_warmup: false },
        { name: 'Triceps Rope Pushdown', sets: 3, reps: '12-15', is_warmup: false },
        { name: 'Dumbbell Lateral Raise', sets: 3, reps: '12-15', is_warmup: false },
      ],
    },
  ];

  it('renders exercise list and does not render "No plan for this day" for valid workout days', () => {
    const handleDayClick = vi.fn();
    render(
      <DaySelector
        sortedDisplayPlan={samplePlan}
        toDayIndex={(dow, idx) => (dow !== undefined ? dow : idx)}
        todayIdx={4}
        completedIds={new Set()}
        handleDayClick={handleDayClick}
        canSwapWorkoutToRest={() => false}
        openWorkoutToRestModal={() => {}}
        workoutLayout={mockWorkoutLayout}
      />
    );

    // Verify Friday shows its exercises
    expect(screen.getByText('• Barbell Bench Press')).toBeInTheDocument();
    expect(screen.getByText('• Incline Dumbbell Press')).toBeInTheDocument();
    expect(screen.getByText('• Triceps Rope Pushdown')).toBeInTheDocument();
    expect(screen.getByText('+1 more exercises')).toBeInTheDocument();

    // Verify START WORKOUT button is present and clickable
    const startBtn = screen.getByText('START WORKOUT');
    expect(startBtn).toBeInTheDocument();
    fireEvent.click(startBtn);
    expect(handleDayClick).toHaveBeenCalledWith(4);

    // Verify "No plan for this day" is NOT present on Friday
    expect(screen.queryByText(/No plan for this day/i)).not.toBeInTheDocument();

    // Monday (placeholder past) shows "Not Started Yet"
    expect(screen.getByText('Not Started Yet')).toBeInTheDocument();
  });

  it('renders "No plan for this day" only when is_placeholder is explicitly true and type is not past', () => {
    const placeholderPlan = [
      {
        day: 'Saturday',
        day_of_week: 5,
        type: 'workout',
        is_placeholder: true,
        focus: 'Legs',
        exercises: [],
      },
    ];

    render(
      <DaySelector
        sortedDisplayPlan={placeholderPlan}
        toDayIndex={(dow, idx) => (dow !== undefined ? dow : idx)}
        todayIdx={4}
        completedIds={new Set()}
        handleDayClick={() => {}}
        canSwapWorkoutToRest={() => false}
        openWorkoutToRestModal={() => {}}
        workoutLayout={mockWorkoutLayout}
      />
    );

    expect(screen.getByText(/No plan for this day/i)).toBeInTheDocument();
    expect(screen.getByText(/Generate a new plan to fill this day/i)).toBeInTheDocument();
  });
});
