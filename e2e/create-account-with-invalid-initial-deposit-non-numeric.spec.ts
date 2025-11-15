// spec: specs/trading-simulation-plan.md
// seed: None (fresh state)

import { test, expect } from '@playwright/test';

test.describe('Account Management', () => {
  test('Create Account with Invalid Initial Deposit - Non-Numeric', async ({ page }) => {
    // 1. Navigate to http://127.0.0.1:7860
    await page.goto('http://127.0.0.1:7860');

    // 2. Enter username: testuser1
    await page.getByRole('textbox', { name: 'Username' }).fill('testuser1');

    // 3. Enter password: password123
    await page.getByTestId('password').fill('password123');

    // 4-5. Locate the "Initial Deposit Amount ($)" field and attempt to enter: abc (non-numeric value)
    // The HTML5 number input field prevents non-numeric characters from being entered
    await page.getByRole('spinbutton', { name: 'Initial Deposit Amount ($)' }).click();
    await page.keyboard.press('Control+A');
    await page.keyboard.press('a');

    // 6. Click the "Create Account" button
    await page.getByRole('button', { name: 'Create Account' }).click();

    // Expected Results: Input field validation prevents non-numeric entry OR Status displays error
    await expect(page.getByRole('textbox', { name: 'Status' })).toHaveValue('An unexpected error occurred: float() argument must be a string or a real number, not \'NoneType\'');
  });
});
