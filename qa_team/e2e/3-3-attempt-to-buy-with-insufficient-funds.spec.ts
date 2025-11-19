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
  test('3.3 Attempt to Buy with Insufficient Funds', async ({ page }) => {
    // Seeding Step: Create user with $1,000
    await createAndLogin(page, 'traderQA', 'password123', 1000);

    // Navigate to Trade tab
    await page.getByRole('tab', { name: 'Trade' }).click();

    // Attempt to execute trade with insufficient funds
    await page.getByLabel('Action').selectOption('BUY');
    await page.getByLabel('Stock Symbol').fill('TSLA');
    await page.getByLabel('Quantity').first().fill('4');
    await page.getByRole('button', { name: 'Execute Trade' }).click();

    // Assert error message
    await expect(page.getByLabel('Status').last()).toHaveValue('Error: Insufficient funds. You need $1,200.00 to buy 4 shares of TSLA, but you only have $1,000.00.');

    // Verify balance is unchanged
    await page.getByRole('tab', { name: 'Portfolio' }).click();
    await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$1,000.00');
  });
});
