import { test, expect } from '@playwright/test';

test.describe('Epic 1: User Account Creation', () => {
  const username = 'newUser123';
  const password = 'password123';

  async function attemptCreation(page, depositAmount) {
    await page.goto('http://127.0.0.1:7860/');
    await page.getByLabel('Username').fill(username);
    await page.getByLabel('Password').fill(password);
    await page.getByLabel('Initial Deposit Amount ($)').fill(depositAmount);
    await page.getByRole('button', { name: 'Create Account' }).click();
  }

  test('1.3 Test Case A: Attempt to create account with zero deposit', async ({ page }) => {
    await attemptCreation(page, '0');
    await expect(page.getByLabel('Status')).toHaveValue('Error: Initial deposit must be a positive number.');
    await expect(page.getByRole('button', { name: 'Create Account' })).toBeVisible();
  });

  test('1.3 Test Case B: Attempt to create account with negative deposit', async ({ page }) => {
    await attemptCreation(page, '-100');
    await expect(page.getByLabel('Status')).toHaveValue('Error: Initial deposit must be a positive number.');
    await expect(page.getByRole('button', { name: 'Create Account' })).toBeVisible();
  });

  test('1.3 Test Case C: Attempt to create account with non-numeric deposit', async ({ page }) => {
    await attemptCreation(page, 'abc');
    // Depending on implementation, this might be prevented by the input type or result in a different error.
    // We test for the specified error message.
    await expect(page.getByLabel('Status')).toHaveValue('Error: Initial deposit must be a positive number.');
    await expect(page.getByRole('button', { name: 'Create Account' })).toBeVisible();
  });
});
