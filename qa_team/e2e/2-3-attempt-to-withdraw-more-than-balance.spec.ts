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
  test('2.3 Attempt to Withdraw More Than Available Balance', async ({ page }) => {
    // Seeding Step: Create user with $1,000
    await createAndLogin(page, 'traderQA', 'password123', 1000);

    // Navigate to Cash Management tab
    await page.getByRole('tab', { name: 'Cash Management' }).click();
    await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$1,000.00');

    // Attempt to withdraw more than available balance
    await page.getByLabel('Amount ($)').fill('1500');
    await page.getByRole('button', { name: 'Withdraw' }).click();

    // Assert error message and unchanged balance
    await expect(page.getByLabel('Status').last()).toHaveValue('Error: Insufficient funds. You cannot withdraw more than your available cash balance of $1,000.00.');
    await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$1,000.00');
  });
});
