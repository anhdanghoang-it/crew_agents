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
  test('3.2 Successful Share Sale', async ({ page }) => {
    // Seeding Step: Create user with $10,000 and buy 10 shares of AAPL
    await createAndLogin(page, 'traderQA', 'password123', 10000);
    await page.getByRole('tab', { name: 'Trade' }).click();
    await page.getByLabel('Action').selectOption('BUY');
    await page.getByLabel('Stock Symbol').fill('AAPL');
    await page.getByLabel('Quantity').first().fill('10');
    await page.getByRole('button', { name: 'Execute Trade' }).click();
    await expect(page.getByLabel('Status').last()).toContainText('Success: Bought 10 shares of AAPL');

    // Execute the sale
    await page.getByLabel('Action').selectOption('SELL');
    await page.getByLabel('Stock Symbol').fill('AAPL');
    await page.getByLabel('Quantity').first().fill('5');
    await page.getByRole('button', { name: 'Execute Trade' }).click();

    // Assert status on Trade tab
    await expect(page.getByLabel('Status').last()).toHaveValue('Success: Sold 5 shares of AAPL at $160.00 each for a total of $800.00.');

    // Navigate to Portfolio and verify changes
    await page.getByRole('tab', { name: 'Portfolio' }).click();
    await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$9,300.00');
    const holdingsTable = page.getByRole('heading', { name: 'Current Holdings' }).locator('xpath=following-sibling::div[1]');
    const updatedRow = holdingsTable.getByRole('row', { name: /AAPL/ });
    await expect(updatedRow).toBeVisible();
    await expect(updatedRow.getByRole('cell').nth(1)).toHaveText('5');
  });
});
