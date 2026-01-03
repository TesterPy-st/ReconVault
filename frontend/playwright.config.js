module.exports = {
  testDir: './e2e',
  webServer: {
    command: 'npm run dev',
    port: 5173,
    reuseExistingServer: !process.env.CI,
  },
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
};
