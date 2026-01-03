module.exports = {
  testEnvironment: 'jsdom',
  collectCoverageFrom: ['src/**/*.{js,jsx}', '!src/main.jsx'],
  coverageThreshold: {
    global: {
      lines: 60,
    },
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(gif|ttf|eot|svg|png)$': '<rootDir>/src/__tests__/__mocks__/fileMock.js',
  },
  transform: {
    '^.+\\.(js|jsx)$': 'babel-jest',
  },
};
