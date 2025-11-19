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
  test('3.5 Attempt to Trade an Invalid Symbol', async ({ page }) => {
    // Seeding Step: Create any user
    await createAndLogin(page, 'traderQA', 'password123', 5000);

    // Navigate to Trade tab
    await page.getByRole('tab', { name: 'Trade' }).click();

    // Attempt to trade an invalid symbol
    await page.getByLabel('Action').selectOption('BUY');
    await page.getByLabel('Stock Symbol').fill('XYZ');
    await page.getByLabel('Quantity').first().fill('1');
    await page.getByRole('button', { name: 'Execute Trade' }).click();

    // Assert error message
    await expect(page.getByLabel('Status').last()).toHaveValue("Error: Invalid stock symbol 'XYZ'. Please use a valid symbol (e.g., AAPL, TSLA, GOOGL).");
  });
});
