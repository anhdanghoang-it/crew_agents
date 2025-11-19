import { test, expect } from '@playwright/test';

async function createAndLogin(page, username, password, deposit) {
  await page.goto('http://127.0.0.1:7860/');
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByLabel('Initial Deposit Amount ($)').fill(deposit.toString());
  await page.getByRole('button', { name: 'Create Account' }).click();
  await expect(page.getByRole('tab', { name: 'Portfolio', selected: true })).toBeVisible();
}

test.describe('Epic 3: User Executes Trades', () => {
  test.beforeEach(async ({ page }) => {
    // Seeding Step: Create user and navigate to Trade tab
    await createAndLogin(page, 'traderQA', 'password123', 5000);
    await page.getByRole('tab', { name: 'Trade' }).click();
    await page.getByLabel('Action').selectOption('BUY');
    await page.getByLabel('Stock Symbol').fill('AAPL');
  });

  const expectedError = 'Error: Quantity must be a positive whole number.';

  test('3.6 Test Case A: Attempt to trade with quantity 0', async ({ page }) => {
    await page.getByLabel('Quantity').first().fill('0');
    await page.getByRole('button', { name: 'Execute Trade' }).click();
    await expect(page.getByLabel('Status').last()).toHaveValue(expectedError);
  });

  test('3.6 Test Case B: Attempt to trade with negative quantity', async ({ page }) => {
    await page.getByLabel('Quantity').first().fill('-5');
    await page.getByRole('button', { name: 'Execute Trade' }).click();
    await expect(page.getByLabel('Status').last()).toHaveValue(expectedError);
  });

  test('3.6 Test Case C: Attempt to trade with decimal quantity', async ({ page }) => {
    await page.getByLabel('Quantity').first().fill('2.5');
    await page.getByRole('button', { name: 'Execute Trade' }).click();
    await expect(page.getByLabel('Status').last()).toHaveValue(expectedError);
  });
});
