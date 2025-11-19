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
  test('3.4 Attempt to Sell More Shares Than Owned', async ({ page }) => {
    // Seeding Step: Create user and buy 5 shares of GOOGL
    await createAndLogin(page, 'traderQA', 'password123', 10000);
    await page.getByRole('tab', { name: 'Trade' }).click();
    await page.getByLabel('Action').selectOption('BUY');
    await page.getByLabel('Stock Symbol').fill('GOOGL');
    await page.getByLabel('Quantity').first().fill('5');
    await page.getByRole('button', { name: 'Execute Trade' }).click();
    await expect(page.getByLabel('Status').last()).toContainText('Success: Bought 5 shares of GOOGL');

    // Attempt to sell more shares than owned
    await page.getByLabel('Action').selectOption('SELL');
    await page.getByLabel('Stock Symbol').fill('GOOGL');
    await page.getByLabel('Quantity').first().fill('10');
    await page.getByRole('button', { name: 'Execute Trade' }).click();

    // Assert error message
    await expect(page.getByLabel('Status').last()).toHaveValue('Error: Insufficient shares. You cannot sell 10 shares of GOOGL as you only own 5.');

    // Verify holdings are unchanged
    await page.getByRole('tab', { name: 'Portfolio' }).click();
    const holdingsTable = page.getByRole('heading', { name: 'Current Holdings' }).locator('xpath=following-sibling::div[1]');
    const googlRow = holdingsTable.getByRole('row', { name: /GOOGL/ });
    await expect(googlRow.getByRole('cell').nth(1)).toHaveText('5');
  });
});
