import { test, expect } from '@playwright/test';

test.describe('Epic 1: User Account Creation', () => {
  test('1.2 Attempt to Create Account with a Duplicate Username', async ({ page }) => {
    // Seeding Step: Create the initial user.
    await page.goto('http://127.0.0.1:7860/');
    await page.getByLabel('Username').fill('existingUser');
    await page.getByLabel('Password').fill('password123');
    await page.getByLabel('Initial Deposit Amount ($)').fill('5000');
    await page.getByRole('button', { name: 'Create Account' }).click();
    await expect(page.getByRole('tab', { name: 'Portfolio' })).toBeVisible();

    // Navigate back to the creation page to attempt creating a duplicate
    await page.goto('http://127.0.0.1:7860/');

    // Attempt to create the same user again
    await page.getByLabel('Username').fill('existingUser');
    await page.getByLabel('Password').fill('any-password');
    await page.getByLabel('Initial Deposit Amount ($)').fill('1000');
    await page.getByRole('button', { name: 'Create Account' }).click();

    // Check for the error message
    await expect(page.getByLabel('Status')).toHaveValue("Error: Username 'existingUser' is already taken. Please choose a different username.");

    // Verify the user remains on the account creation screen
    await expect(page.getByRole('button', { name: 'Create Account' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Portfolio' })).not.toBeVisible();
  });
});
