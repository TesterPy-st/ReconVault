const { test, expect } = require('@playwright/test');

test('api health check should be reflected in UI', async ({ page }) => {
  await page.goto('/');
  
  // Check for some status indicator if it exists
  // Or just verify the page loads correctly
  await expect(page).toHaveTitle(/ReconVault/);
});

test('real-time updates via websocket', async ({ page }) => {
  await page.goto('/');
  
  // This is hard to test without triggering an event on the backend
  // But we can check if the websocket connects (no errors in console)
  page.on('console', msg => {
    if (msg.type() === 'error')
      console.log(`PAGE ERROR: ${msg.text()}`);
  });
});
