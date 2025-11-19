import { test, expect } from '@playwright/test';

async function createAndLogin(page, username, password, deposit) {
  await page.goto('http://127.0.0.1:7860/');
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByLabel('Initial Deposit Amount ($)').fill(deposit.toString());
  await page.getByRole('button', { name: 'Create Account' }).click();
  await expect(page.getByRole('tab', { name: 'Portfolio', selected: true })).toBeVisible();
}

test.describe('Epic 2: User Manages Cash Balance', () => {
  test.beforeEach(async ({ page }) => {
    // Seeding Step: Create user with $1000
    await createAndLogin(page, 'traderQA', 'password123', 1000);
    await page.getByRole('tab', { name: 'Cash Management' }).click();
  });

  const expectedError = 'Error: Amount must be a positive number.';

  test('2.4 Attempt to deposit a negative amount', async ({ page }) => {
    await page.getByLabel('Amount ($)').fill('-50');
    await page.getByRole('button', { name: 'Deposit' }).click();
    await expect(page.getByLabel('Status').last()).toHaveValue(expectedError);
    await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$1,000.00');
  });

  test('2.4 Attempt to withdraw a negative amount', async ({ page }) => {
    await page.getByLabel('Amount ($)').fill('-50');
    await page.getByRole('button', { name: 'Withdraw' }).click();
    await expect(page.getByLabel('Status').last()).toHaveValue(expectedError);
    await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$1,000.00');
  });

  test('2.4 Attempt to deposit zero', async ({ page }) => {
    await page.getByLabel('Amount ($)').fill('0');
    await page.getByRole('button', { name: 'Deposit' }).click();
    await expect(page.getByLabel('Status').last()).toHaveValue(expectedError);
    await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$1,000.00');
  });

  test('2.4 Attempt to withdraw zero', async ({ page }) => {
    await page.getByLabel('Amount ($)').fill('0');
    await page.getByRole('button', { name: 'Withdraw' }).click();
    await expect(page.getByLabel('Status').last()).toHaveValue(expectedError);
    await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$1,000.00');
  });
});
