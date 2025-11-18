// Global Jest setup for backend tests

// Mock environment variables
process.env.JWT_SECRET = process.env.JWT_SECRET || 'test_jwt_secret';
process.env.MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/elevate_test';

// Set test environment
process.env.NODE_ENV = 'test';

// Mock external services during tests
jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn(),
  create: jest.fn(() => ({
    interceptors: {
      request: { use: jest.fn(), eject: jest.fn() },
      response: { use: jest.fn(), eject: jest.fn() }
    },
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn()
  }))
}));

// Mock JWT for testing
jest.mock('jsonwebtoken', () => ({
  sign: jest.fn().mockReturnValue('test-jwt-token'),
  verify: jest.fn().mockReturnValue({ user: { id: 'test-user-id' } }),
}));

// Setup completed
console.log('Global test setup completed');