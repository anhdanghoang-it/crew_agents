// spec: specs/trading-simulation-plan.md
// seed: tests/seed.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Account Management', () => {
  test('Create New Account with Valid Initial Deposit', async ({ page }) => {
    // 1. Navigate to http://127.0.0.1:7860
    await page.goto('http://127.0.0.1:7860');
    
    // 2-3. Locate the "Username" textbox and enter username: trader123
    await page.getByLabel('Username').fill('trader123');
    
    // 4-5. Locate the "Password" textbox and enter password: password123
    await page.getByLabel('Password').fill('password123');
    
    // 6-7. Locate the "Initial Deposit Amount ($)" number input and enter amount: 10000
    await page.getByLabel('Initial Deposit Amount ($)').fill('10000');
    
    // 8. Click the "Create Account" button
    await page.getByRole('button', { name: 'Create Account' }).click();
    
    // 9. Navigate to the "Portfolio" tab (already on Portfolio tab after account creation)
    
    // Verify Cash Balance shows: $10,000.00
    await expect(page.getByRole('textbox', { name: 'Cash Balance ($)' })).toHaveValue('$10,000.00');
    
    // Verify Total Portfolio Value shows: $10,000.00
    await expect(page.getByRole('textbox', { name: 'Total Portfolio Value ($)' })).toHaveValue('$10,000.00');
    
    // Verify Total Profit / Loss shows: $0.00
    await expect(page.getByRole('textbox', { name: 'Total Profit / Loss ($)' })).toHaveValue('$0.00');
    
    // Navigate to History tab to verify transaction
    await page.getByRole('tab', { name: 'History' }).click();
    
    // Verify Transaction History shows one DEPOSIT entry for $10,000.00
    await expect(page.getByText('DEPOSIT')).toBeVisible();
    await expect(page.getByText('$10,000.00')).toBeVisible();
  });
});
