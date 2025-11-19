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
  test('4.3 View Empty Portfolio and Initial History for a New User', async ({ page }) => {
    // Seeding Step: Create a new user with $10,000
    await createAndLogin(page, 'traderQA', 'password123', 10000);

    // Assertions on the Portfolio tab
    await expect(page.getByRole('tab', { name: 'Portfolio', selected: true })).toBeVisible();

    await expect(page.getByLabel('Total Portfolio Value ($)')).toHaveValue('$10,000.00');
    await expect(page.getByLabel('Total Profit / Loss ($)')).toHaveValue('$0.00');
    await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$10,000.00');

    const holdingsTable = page.getByRole('heading', { name: 'Current Holdings' }).locator('xpath=following-sibling::div[1]');
    // Expect no rows other than the header
    await expect(holdingsTable.getByRole('row')).toHaveCount(1);
    await expect(holdingsTable).not.toContainText('AAPL'); // Check for absence of any stock

    // Navigate to History tab and check for initial deposit
    await page.getByRole('tab', { name: 'History' }).click();
    const historyTable = page.locator('p:has-text("Transaction History")').locator('xpath=following-sibling::div[1]');
    
    // Expect only one transaction row + header row
    await expect(historyTable.getByRole('row')).toHaveCount(2);

    const depositRow = historyTable.getByRole('row').nth(1);
    await expect(depositRow).toContainText('DEPOSIT');
    await expect(depositRow).toContainText('$10,000.00');
  });
});
