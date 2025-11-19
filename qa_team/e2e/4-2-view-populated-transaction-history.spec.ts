import { test, expect } from '@playwright/test';

async function createAndLogin(page, username, password, deposit) {
  await page.goto('http://127.0.0.1:7860/');
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByLabel('Initial Deposit Amount ($)').fill(deposit.toString());
  await page.getByRole('button', { name: 'Create Account' }).click();
  await expect(page.getByRole('tab', { name: 'Portfolio', selected: true })).toBeVisible();
}

test.describe('Epic 4: User Views Portfolio and History', () => {
  test('4.2 View Populated Transaction History in Correct Order', async ({ page }) => {
    // Seeding Steps
    // 1. Initial Deposit: $20,000
    await createAndLogin(page, 'traderQA', 'password123', 20000);

    // 2. Buy 10 AAPL at $150
    await page.getByRole('tab', { name: 'Trade' }).click();
    await page.getByLabel('Action').selectOption('BUY');
    await page.getByLabel('Stock Symbol').fill('AAPL');
    await page.getByLabel('Quantity').first().fill('10');
    await page.getByRole('button', { name: 'Execute Trade' }).click();
    await expect(page.getByLabel('Status').last()).toContainText('Success: Bought 10 shares of AAPL');

    // 3. Withdraw $1,000
    await page.getByRole('tab', { name: 'Cash Management' }).click();
    await page.getByLabel('Amount ($)').fill('1000');
    await page.getByRole('button', { name: 'Withdraw' }).click();
    await expect(page.getByLabel('Status').last()).toContainText('Success: $1,000.00 withdrawn');

    // 4. Sell 5 GOOGL at $100 (requires owning them first)
    // The plan assumes shares are present. Let's add a buy for them first.
    await page.getByRole('tab', { name: 'Trade' }).click();
    await page.getByLabel('Stock Symbol').fill('GOOGL');
    await page.getByLabel('Quantity').first().fill('5');
    await page.getByRole('button', { name: 'Execute Trade' }).click();
    await expect(page.getByLabel('Status').last()).toContainText('Success: Bought 5 shares of GOOGL');
    // Now, sell them
    await page.getByLabel('Action').selectOption('SELL');
    await page.getByLabel('Stock Symbol').fill('GOOGL');
    await page.getByLabel('Quantity').first().fill('5');
    await page.getByRole('button', { name: 'Execute Trade' }).click();
    await expect(page.getByLabel('Status').last()).toContainText('Success: Sold 5 shares of GOOGL');

    // Navigate to History and verify transactions
    await page.getByRole('tab', { name: 'History' }).click();
    const historyTable = page.locator('p:has-text("Transaction History")').locator('xpath=following-sibling::div[1]');
    const rows = historyTable.getByRole('row');

    // Total 5 transactions: DEPOSIT, BUY AAPL, WITHDRAW, BUY GOOGL, SELL GOOGL
    await expect(rows).toHaveCount(6); // 1 header + 5 transactions

    // Verify reverse chronological order
    await expect(rows.nth(1)).toContainText('SELL');
    await expect(rows.nth(1)).toContainText('GOOGL');
    await expect(rows.nth(1)).toContainText('5');
    await expect(rows.nth(1)).toContainText('$100.00');
    await expect(rows.nth(1)).toContainText('$500.00');

    await expect(rows.nth(2)).toContainText('BUY');
    await expect(rows.nth(2)).toContainText('GOOGL');

    await expect(rows.nth(3)).toContainText('WITHDRAWAL');
    await expect(rows.nth(3)).toContainText('$1,000.00');

    await expect(rows.nth(4)).toContainText('BUY');
    await expect(rows.nth(4)).toContainText('AAPL');

    await expect(rows.nth(5)).toContainText('DEPOSIT');
    await expect(rows.nth(5)).toContainText('$20,000.00');
    // Verify null/N/A values for deposit
    await expect(rows.nth(5).getByRole('cell').nth(2)).toHaveText(/null|N\/A/);
    await expect(rows.nth(5).getByRole('cell').nth(3)).toHaveText(/null|N\/A/);
    await expect(rows.nth(5).getByRole('cell').nth(4)).toHaveText(/null|N\/A/);
  });
});
