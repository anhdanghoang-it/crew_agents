// spec: specs/trading-simulation-plan.md
// seed: e2e/seed.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Account Management', () => {
  test('Create New Account with Valid Initial Deposit', async ({ page }) => {
    // Seed: Create account with initial deposit
    await page.goto('http://127.0.0.1:7860');
    await page.getByLabel('Username').fill('trader123');
    await page.getByLabel('Password').fill('password123');
    await page.getByLabel('Initial Deposit Amount ($)').fill('10000');
    await page.getByRole('button', { name: 'Create Account' }).click();

    // 1. Verify Cash Balance shows: $10,000.00
    await expect(page.getByRole('textbox', { name: 'Cash Balance ($)' })).toHaveValue('$10,000.00');
    
    // 2. Verify Total Portfolio Value shows: $10,000.00
    await expect(page.getByRole('textbox', { name: 'Total Portfolio Value ($)' })).toHaveValue('$10,000.00');
    
    // 3. Verify Total Profit / Loss shows: $0.00
    await expect(page.getByRole('textbox', { name: 'Total Profit / Loss ($)' })).toHaveValue('$0.00');
    
    // 4. Navigate to History tab to verify transaction
    await page.getByRole('tab', { name: 'History' }).click();
    
    // 5. Verify Transaction History shows DEPOSIT entry
    await expect(page.getByText('DEPOSIT')).toBeVisible();
    
    // 6. Verify Transaction History shows $10,000.00 entry
    await expect(page.getByText('$10,000.00')).toBeVisible();
  });
});
