import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Auth } from '@/components/Auth.jsx';

// Mock the auth context and API
jest.mock('@/contexts/AuthContext.jsx', () => ({
  useAuth: () => ({
    login: jest.fn().mockResolvedValue({}),
    register: jest.fn().mockResolvedValue({}),
  }),
}));

// Mock toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('Auth Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form by default', () => {
    render(
      <MemoryRouter>
        <Auth />
      </MemoryRouter>
    );

    expect(screen.getByText(/Welcome Back/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByText(/Sign In/i)).toBeInTheDocument();
    expect(screen.getByText(/Don't have an account\?/i)).toBeInTheDocument();
  });

  test('switches to registration form when sign up is clicked', () => {
    render(
      <MemoryRouter>
        <Auth />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText(/Sign up/i));

    expect(screen.getByText(/Start Your Journey/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Fitness Goal/i)).toBeInTheDocument();
    expect(screen.getByText(/Create Account/i)).toBeInTheDocument();
    expect(screen.getByText(/Already have an account\?/i)).toBeInTheDocument();
  });

  test('submits login form', async () => {
    const mockLogin = jest.fn().mockResolvedValue({});
    jest.mock('@/contexts/AuthContext.jsx', () => ({
      useAuth: () => ({
        login: mockLogin,
        register: jest.fn(),
      }),
    }));

    render(
      <MemoryRouter>
        <Auth />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Password/i), {
      target: { value: 'password123' },
    });

    fireEvent.click(screen.getByText(/Sign In/i));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  test('submits registration form', async () => {
    const mockRegister = jest.fn().mockResolvedValue({});
    jest.mock('@/contexts/AuthContext.jsx', () => ({
      useAuth: () => ({
        login: jest.fn(),
        register: mockRegister,
      }),
    }));

    render(
      <MemoryRouter>
        <Auth />
      </MemoryRouter>
    );

    // Switch to register form
    fireEvent.click(screen.getByText(/Sign up/i));

    fireEvent.change(screen.getByLabelText(/Name/i), {
      target: { value: 'Test User' },
    });
    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Password/i), {
      target: { value: 'password123' },
    });

    fireEvent.click(screen.getByText(/Create Account/i));

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123',
        fitnessGoal: 'weight-loss',
      });
    });
  });

  test('shows error for login failure', async () => {
    const mockLogin = jest.fn().mockRejectedValue(new Error('Invalid credentials'));
    const toastErrorSpy = jest.spyOn(require('sonner').toast, 'error');

    jest.mock('@/contexts/AuthContext.jsx', () => ({
      useAuth: () => ({
        login: mockLogin,
        register: jest.fn(),
      }),
    }));

    render(
      <MemoryRouter>
        <Auth />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Password/i), {
      target: { value: 'wrongpassword' },
    });

    fireEvent.click(screen.getByText(/Sign In/i));

    await waitFor(() => {
      expect(toastErrorSpy).toHaveBeenCalledWith('Invalid credentials');
    });
  });
});