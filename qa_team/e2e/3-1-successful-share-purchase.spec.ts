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
  test('3.1 Successful Share Purchase', async ({ page }) => {
    // Seeding Step: Create user with $10,000
    await createAndLogin(page, 'traderQA', 'password123', 10000);

    // Navigate to Trade tab
    await page.getByRole('tab', { name: 'Trade' }).click();

    // Execute trade
    await page.getByLabel('Action').selectOption('BUY');
    await page.getByLabel('Stock Symbol').fill('AAPL');
    await page.getByLabel('Quantity').first().fill('10');
    await page.getByRole('button', { name: 'Execute Trade' }).click();

    // Assert status on Trade tab
    await expect(page.getByLabel('Status').last()).toHaveValue('Success: Bought 10 shares of AAPL at $150.00 each for a total of $1,500.00.');

    // Navigate to Portfolio and verify changes
    await page.getByRole('tab', { name: 'Portfolio' }).click();
    await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$8,500.00');
    const holdingsTable = page.getByRole('heading', { name: 'Current Holdings' }).locator('xpath=following-sibling::div[1]');
    const newRow = holdingsTable.getByRole('row', { name: /AAPL/ });
    await expect(newRow).toBeVisible();
    await expect(newRow.getByRole('cell').nth(1)).toHaveText('10');
  });
});
