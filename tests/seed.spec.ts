import { test, expect } from '@playwright/test';

test.describe('login', () => {
  test('seed', async ({ page }) => {
    // generate code here.
      await page.goto('http://127.0.0.1:7860');
      await page.getByLabel('Username').fill('trader123');
      await page.getByLabel('Password').fill('password123');
      await page.getByLabel('Initial Deposit Amount ($)').fill('10000');
      await page.getByRole('button', { name: 'Create Account' }).click();

      // Expect: Cash balance and portfolio value
      await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$10,000.00');
      await expect(page.getByLabel('Total Portfolio Value ($)')).toHaveValue('$10,000.00');
  });
});
