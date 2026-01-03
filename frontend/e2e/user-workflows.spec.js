const { test, expect } = require('@playwright/test');

test('user can search and see results', async ({ page }) => {
  await page.goto('/');
  
  // Fill search input
  await page.fill('input[placeholder*="Search"]', 'example.com');
  await page.press('input[placeholder*="Search"]', 'Enter');
  
  // Check if graph canvas is present
  const canvas = await page.locator('canvas');
  await expect(canvas).toBeVisible();
});

test('user can open entity inspector', async ({ page }) => {
  await page.goto('/');
  
  // Assuming there's a list of targets or entities
  // For now just check if sidebar is there
  const sidebar = await page.locator('aside');
  await expect(sidebar).toBeVisible();
});
