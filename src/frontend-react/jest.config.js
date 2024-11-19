const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './', // Path to your Next.js app
});

const customJestConfig = {
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleDirectories: ['node_modules', '<rootDir>/src'], // Support absolute imports from `src`
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1', // Map `@` alias to `./src/`
  },
};

module.exports = createJestConfig(customJestConfig);
