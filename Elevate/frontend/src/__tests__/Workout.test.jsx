import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Workout } from '@/components/Workout.jsx';

// Mock the user data context
jest.mock('@/contexts/UserDataContext.jsx', () => ({
  useUserData: () => ({
    userProfile: { fitnessGoal: 'strength', fitnessLevel: 'intermediate' },
  }),
}));

// Mock the ML API
jest.mock('@/services/api.js', () => ({
  mlAPI: {
    recommendWorkout: jest.fn().mockResolvedValue({
      data: {
        exercises: [
          {
            name: 'Push-ups',
            sets: 3,
            reps: 15,
            hints: ['Keep your back straight', 'Lower chest to ground']
          }
        ]
      }
    }),
  },
}));

// Mock toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('Workout Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    render(
      <MemoryRouter>
        <Workout />
      </MemoryRouter>
    );

    expect(screen.getByText(/Generating your personalized workout plan/i)).toBeInTheDocument();
  });

  test('renders workout plan after loading', async () => {
    render(
      <MemoryRouter>
        <Workout />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Exercise 1 of 1/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Push-ups/i)).toBeInTheDocument();
    expect(screen.getByText(/3 sets × 15 reps/i)).toBeInTheDocument();
  });

  test('handles API error gracefully', async () => {
    (require('@/services/api.js').mlAPI.recommendWorkout).mockRejectedValue(
      new Error('API Error')
    );

    render(
      <MemoryRouter>
        <Workout />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Workout/i)).toBeInTheDocument();
    });
  });

  test('allows rep counting', async () => {
    render(
      <MemoryRouter>
        <Workout />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Push-ups/i)).toBeInTheDocument();
    });

    // Find the "Count Rep" button and click it
    const countRepButton = screen.getByText(/Count Rep/i);
    expect(countRepButton).toBeInTheDocument();

    // Initially rep count should be 0
    expect(screen.getByText(/0/)).toBeInTheDocument();

    fireEvent.click(countRepButton);

    // After clicking, rep count should be 1
    await waitFor(() => {
      expect(screen.getByText(/1/)).toBeInTheDocument();
    });
  });

  test('refreshes workout plan when button is clicked', async () => {
    const mockRecommendWorkout = jest.fn().mockResolvedValue({
      data: {
        exercises: [
          {
            name: 'Squats',
            sets: 4,
            reps: 12,
            hints: ['Feet shoulder-width apart', 'Knees behind toes']
          }
        ]
      }
    });

    jest.mock('@/services/api.js', () => ({
      mlAPI: {
        recommendWorkout: mockRecommendWorkout,
      },
    }));

    render(
      <MemoryRouter>
        <Workout />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Exercise 1 of 1/i)).toBeInTheDocument();
    });

    // Find and click the refresh button
    const refreshButton = screen.getByRole('button', { name: /Refresh Plan/i });
    expect(refreshButton).toBeInTheDocument();
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(mockRecommendWorkout).toHaveBeenCalledTimes(2);
    });
  });
});