import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MealPlan } from '@/components/MealPlan';

// Mock the user data context
jest.mock('@/context/UserDataContext', () => ({
  useUserData: () => ({
    userProfile: { fitnessGoal: 'muscle-gain', dietPreference: 'high-protein' },
  }),
}));

// Mock the ML API
jest.mock('@/services/api', () => ({
  mlAPI: {
    recommendMeal: jest.fn().mockResolvedValue({
      data: {
        meals: [
          {
            id: 1,
            type: 'Breakfast',
            name: 'Protein Oatmeal Bowl',
            image: 'test-image-url',
            calories: 450,
            protein: 25,
            carbs: 55,
            fats: 12
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

// Mock ImageWithFallback
jest.mock('@/components/figma/ImageWithFallback', () => ({
  ImageWithFallback: ({ src, alt }: { src: string; alt: string }) => (
    <img src={src} alt={alt} data-testid="image" />
  ),
}));

describe('MealPlan Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    render(
      <MemoryRouter>
        <MealPlan />
      </MemoryRouter>
    );

    expect(screen.getByText(/Generating your personalized meal plan/i)).toBeInTheDocument();
  });

  test('renders meal plan after loading', async () => {
    render(
      <MemoryRouter>
        <MealPlan />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Today's Meal Plan/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Protein Oatmeal Bowl/i)).toBeInTheDocument();
    expect(screen.getByText(/450/i)).toBeInTheDocument();
    expect(screen.getByText(/25g/i)).toBeInTheDocument();
  });

  test('handles API error gracefully', async () => {
    (require('@/services/api').mlAPI.recommendMeal as jest.Mock).mockRejectedValue(
      new Error('API Error')
    );

    render(
      <MemoryRouter>
        <MealPlan />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Meal Plan/i)).toBeInTheDocument();
    });
  });

  test('refreshes meal plan when button is clicked', async () => {
    const mockRecommendMeal = jest.fn().mockResolvedValue({
      data: {
        meals: [
          {
            id: 1,
            type: 'Breakfast',
            name: 'Greek Yogurt & Berries',
            image: 'test-image-url',
            calories: 200,
            protein: 15,
            carbs: 25,
            fats: 3
          }
        ]
      }
    });

    jest.mock('@/services/api', () => ({
      mlAPI: {
        recommendMeal: mockRecommendMeal,
      },
    }));

    render(
      <MemoryRouter>
        <MealPlan />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Today's Meal Plan/i)).toBeInTheDocument();
    });

    // Find and click the refresh button
    const refreshButton = screen.getByRole('button', { name: /Refresh Plan/i });
    expect(refreshButton).toBeInTheDocument();
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(mockRecommendMeal).toHaveBeenCalledTimes(2);
    });
  });
});