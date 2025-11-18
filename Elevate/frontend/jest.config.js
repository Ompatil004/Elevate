module.exports = {
  testEnvironment: 'jsdom',
  testMatch: [
    '**/__tests__/**/*.{js,jsx,ts,tsx}',
    '**/*.(test|spec).{js,jsx,ts,tsx}'
  ],
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/index.{js,jsx,ts,tsx}',
    '!src/**/types/**',
    '!**/node_modules/**',
    '!**/coverage/**'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html']
};