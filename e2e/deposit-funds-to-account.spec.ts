// spec: specs/trading-simulation-plan.md
// seed: tests/seed.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Cash Management', () => {
  test('Deposit Funds to Account', async ({ page }) => {
    // 1. Navigate to application (user logged in with $10,000 balance) - handled by seed
    await page.goto('http://127.0.0.1:7860');
    await page.getByLabel('Username').fill('trader123');
    await page.getByLabel('Password').fill('password123');
    await page.getByLabel('Initial Deposit Amount ($)').fill('10000');
    await page.getByRole('button', { name: 'Create Account' }).click();

    // 2. Click the "Cash Management" tab
    await page.getByRole('tab', { name: 'Cash Management' }).click();

    // 3. Verify "Current Cash Balance" displays: $10,000.00
    await expect(page.getByRole('textbox', { name: 'Current Cash Balance' })).toHaveValue('$10,000.00');

    // 4-5. Locate the "Amount ($)" number input and enter amount: 2000
    await page.getByRole('spinbutton', { name: 'Amount ($)' }).fill('2000');

    // 6. Click the "Deposit" button
    await page.getByRole('button', { name: 'Deposit' }).click();

    // Verify Current Cash Balance updates to: $12,000.00
    await expect(page.getByRole('textbox', { name: 'Current Cash Balance' })).toHaveValue('$12,000.00');

    // 7. Navigate to "Portfolio" tab to verify
    await page.getByRole('tab', { name: 'Portfolio' }).click();

    // Verify Portfolio tab shows Cash Balance: $12,000.00
    await expect(page.getByRole('textbox', { name: 'Cash Balance ($)' })).toHaveValue('$12,000.00');

    // Verify Total Portfolio Value increases to: $12,000.00
    await expect(page.getByRole('textbox', { name: 'Total Portfolio Value ($)' })).toHaveValue('$12,000.00');
  });
});
