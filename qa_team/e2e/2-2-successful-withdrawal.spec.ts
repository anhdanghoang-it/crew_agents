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
  test('2.2 Successful Withdrawal', async ({ page }) => {
    // Seeding Step: Create user with $7,000
    await createAndLogin(page, 'traderQA', 'password123', 7000);

    // Navigate to Cash Management tab
    await page.getByRole('tab', { name: 'Cash Management' }).click();
    await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$7,000.00');

    // Perform withdrawal
    await page.getByLabel('Amount ($)').fill('1500');
    await page.getByRole('button', { name: 'Withdraw' }).click();

    // Assert status and balance update
    await expect(page.getByLabel('Status').last()).toHaveValue('Success: $1,500.00 withdrawn. Your new cash balance is $5,500.00.');
    await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$5,500.00');

    // Navigate to History and verify transaction
    await page.getByRole('tab', { name: 'History' }).click();
    const historyTable = page.locator('p:has-text("Transaction History")').locator('xpath=following-sibling::div[1]');
    const firstRow = historyTable.getByRole('row').nth(1);
    await expect(firstRow).toContainText('WITHDRAWAL');
    await expect(firstRow).toContainText('$1,500.00');
  });
});
