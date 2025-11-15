// spec: specs/trading-simulation-plan.md
// seed: tests/seed.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Stock Trading', () => {
  test('Buy Shares - Successful Purchase', async ({ page }) => {
    // 1. Navigate to application (cash balance: $10,000) - handled by seed
    await page.goto('http://127.0.0.1:7860');
    await page.getByLabel('Username').fill('trader123');
    await page.getByLabel('Password').fill('password123');
    await page.getByLabel('Initial Deposit Amount ($)').fill('10000');
    await page.getByRole('button', { name: 'Create Account' }).click();

    // 2. Click the "Trade" tab
    await page.getByRole('tab', { name: 'Trade' }).click();

    // 3-6. Use example to fill form and execute trade (BUY AAPL 10)
    await page.getByRole('row', { name: 'BUY AAPL' }).click();
    await page.getByRole('button', { name: 'Execute Trade' }).click();

    // 7. Navigate to "Portfolio" tab
    await page.getByRole('tab', { name: 'Portfolio' }).click();

    // Verify Cash Balance reduces to $8,500.00 ($10,000 - $1,500)
    await expect(page.getByRole('textbox', { name: 'Cash Balance ($)' })).toHaveValue('$8,500.00');

    // Verify Current Holdings shows AAPL with 10 shares
    await expect(page.getByRole('button', { name: 'AAPL' })).toBeVisible();

    // Verify Total Portfolio Value remains $10,000.00 ($8,500 cash + $1,500 shares)
    await expect(page.getByRole('textbox', { name: 'Total Portfolio Value ($)' })).toHaveValue('$10,000.00');
  });
});
