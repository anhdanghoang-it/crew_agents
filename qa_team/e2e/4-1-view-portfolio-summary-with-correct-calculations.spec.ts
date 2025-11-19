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
  test('4.1 View Portfolio Summary with Correct Calculations', async ({ page }) => {
    // Seeding Steps:
    // 1. Net Deposit of $10,000, but end with cash balance of $5,000.
    //    This means we start with $10k and spend $5k on stocks.
    // 2. Buy 10 AAPL @ $150 ($1500) and 5 TSLA @ $300 ($1500) - this doesn't match $5k spend.
    //    Correcting spend: (10 * $150) + (5 * $300) = $1500 + $1500 = $3000. 
    //    To have $5k cash left from $10k initial, we need to spend $5k. Let's adjust quantities.
    //    Let's buy 10 AAPL ($1500) and then something else for $3500.
    //    We'll follow the plan's holdings: 10 AAPL, 5 TSLA. The cash must have been $5k after purchases.
    //    So, Initial Deposit = $5000 (cash) + $1500 (AAPL) + $1500 (TSLA) = $8000.
    //    P/L = (Current Value $8k) - (Net Deposit $8k) = $0. The plan says -$2k P/L. 
    //    This means Net Deposit must be $10k. So, Initial Deposit = $10k. Cash left = $10k - $3k = $7k. The plan is inconsistent.
    //    I will follow the explicit expected results and seed state.
    //    Seed: Cash $5k, 10 AAPL, 5 TSLA. Total value = 5000 + (10*150) + (5*300) = 5000 + 1500 + 1500 = $8000.
    //    P/L = Current Value ($8000) - Net Deposit ($10000) = -$2000. This works.

    await createAndLogin(page, 'traderQA', 'password123', 10000);

    // Buy 10 AAPL
    await page.getByRole('tab', { name: 'Trade' }).click();
    await page.getByLabel('Action').selectOption('BUY');
    await page.getByLabel('Stock Symbol').fill('AAPL');
    await page.getByLabel('Quantity').first().fill('10');
    await page.getByRole('button', { name: 'Execute Trade' }).click();
    await expect(page.getByLabel('Status').last()).toContainText('Success: Bought 10 shares of AAPL');

    // Buy 5 TSLA
    await page.getByLabel('Stock Symbol').fill('TSLA');
    await page.getByLabel('Quantity').first().fill('5');
    await page.getByRole('button', { name: 'Execute Trade' }).click();
    await expect(page.getByLabel('Status').last()).toContainText('Success: Bought 5 shares of TSLA');

    // Withdraw to get cash to $5000. Cash is now 10000 - 1500 - 1500 = 7000. Withdraw 2000.
    await page.getByRole('tab', { name: 'Cash Management' }).click();
    await page.getByLabel('Amount ($)').fill('2000');
    await page.getByRole('button', { name: 'Withdraw' }).click();
    await expect(page.getByLabel('Status').last()).toContainText('Success: $2,000.00 withdrawn');

    // Navigate to portfolio and verify all values
    await page.getByRole('tab', { name: 'Portfolio' }).click();
    await page.getByRole('button', { name: 'Refresh' }).click();

    await expect(page.getByLabel('Total Portfolio Value ($)')).toHaveValue('$8,000.00');
    await expect(page.getByLabel('Total Profit / Loss ($)')).toHaveValue('-$2,000.00');
    await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$5,000.00');

    const holdingsTable = page.getByRole('heading', { name: 'Current Holdings' }).locator('xpath=following-sibling::div[1]');
    const aaplRow = holdingsTable.getByRole('row', { name: /AAPL/ });
    const tslaRow = holdingsTable.getByRole('row', { name: /TSLA/ });

    await expect(aaplRow).toBeVisible();
    await expect(aaplRow).toContainText('10');
    await expect(aaplRow).toContainText('$150.00');
    await expect(aaplRow).toContainText('$1,500.00');

    await expect(tslaRow).toBeVisible();
    await expect(tslaRow).toContainText('5');
    await expect(tslaRow).toContainText('$300.00');
    await expect(tslaRow).toContainText('$1,500.00');
  });
});
