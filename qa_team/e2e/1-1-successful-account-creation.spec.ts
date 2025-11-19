import { test, expect } from '@playwright/test';

test.describe('Epic 1: User Account Creation', () => {
  test('1.1 Successful Account Creation (Happy Path)', async ({ page }) => {
    await page.goto('http://127.0.0.1:7860/');

    // Fill out the account creation form
    await page.getByLabel('Username').fill('traderQA');
    await page.getByLabel('Password').fill('password123');
    await page.getByLabel('Initial Deposit Amount ($)').fill('10000');
    await page.getByRole('button', { name: 'Create Account' }).click();

    // Check for success message on the creation screen
    await expect(page.getByLabel('Status')).toHaveValue("Success: Account 'traderQA' created with an initial deposit of $10,000.00.", { timeout: 10000 });

    // Verify UI transitions to the main interface and Portfolio tab is active
    await expect(page.getByRole('tab', { name: 'Portfolio', selected: true })).toBeVisible();

    // Verify values on the Portfolio tab
    await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$10,000.00');
    await expect(page.getByLabel('Total Portfolio Value ($)')).toHaveValue('$10,000.00');
    await expect(page.getByLabel('Total Profit / Loss ($)')).toHaveValue('$0.00');
  });
});
