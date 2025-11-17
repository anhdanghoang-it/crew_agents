import { test, expect, Page } from '@playwright/test';

const BASE_URL = 'http://127.0.0.1:7860/';

async function createAccount(page: Page, username: string, password: string, deposit: number) {
    await page.goto(BASE_URL);
    await page.getByLabel('Username').fill(username);
    await page.getByLabel('Password').fill(password);
    await page.getByLabel('Initial Deposit Amount ($)').fill(deposit.toString());
    await page.getByRole('button', { name: 'Create Account' }).click();
}

test.describe('Epic 1: Account Management & Creation', () => {

    test('1.1 Create New Account Successfully (Happy Path)', async ({ page }) => {
        await createAccount(page, 'traderQA', 'password123', 10000);

        // await expect(page.getByLabel('Status').first()).toHaveValue("Success: Account 'traderQA' created with an initial deposit of $10,000.00.");

        // Verify Portfolio tab
        await page.getByRole('tab', { name: 'Portfolio' }).click();
        await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$10,000.00');
        await expect(page.getByLabel('Total Portfolio Value ($)')).toHaveValue('$10,000.00');
        await expect(page.getByLabel('Total Profit / Loss ($)')).toHaveValue('$0.00');

        // Verify History tab
        await page.getByRole('tab', { name: 'History' }).click();
        const historyRow = page.locator('.gr-table tr').nth(1);
        await expect(page.getByRole('button', { name: 'DEPOSIT' })).toContainText('DEPOSIT');
        await expect(page.getByRole('button', { name: '$' })).toContainText('$10,000.00');
    });

    test('1.2 Attempt to Create Account with a Non-Unique Username', async ({ page }) => {
        // Seeding step: create an account first
        await createAccount(page, 'traderQA', 'password123', 5000);
        await expect(page.getByLabel('Status').first()).toHaveValue("Success: Account 'traderQA' created with an initial deposit of $5,000.00.");

        // Attempt to create the same account again
        await createAccount(page, 'traderQA', 'anotherpass', 2000);
        await expect(page.getByLabel('Status').first()).toHaveValue("Error: Username 'traderQA' is already taken. Please choose a different username.");
    });

    test('1.3 Attempt to Create Account with Invalid Initial Deposit', async ({ page }) => {
        await page.goto(BASE_URL);

        // Attempt with negative value
        await page.getByLabel('Username').fill('invalidTrader');
        await page.getByLabel('Password').fill('password123');
        await page.getByLabel('Initial Deposit Amount ($)').fill('-100');
        await page.getByRole('button', { name: 'Create Account' }).click();
        await expect(page.getByLabel('Status').first()).toHaveValue("Error: Initial deposit must be a positive number.");

        // Attempt with zero
        await page.getByLabel('Initial Deposit Amount ($)').fill('0');
        await page.getByRole('button', { name: 'Create Account' }).click();
        await expect(page.getByLabel('Status').first()).toHaveValue("Error: Initial deposit must be a positive number.");
    });
});

test.describe('Epic 2: Cash Management', () => {

    test('2.1 Successful Deposit and Balance Update', async ({ page }) => {
        await createAccount(page, 'cashTrader1', 'password123', 10000);
        await page.getByRole('tab', { name: 'Cash Management' }).click();

        await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$10,000.00');
        
        await page.getByLabel('Amount ($)').fill('2000');
        await page.getByRole('button', { name: 'Deposit' }).click();

        await expect(page.getByRole('textbox', { name: 'Status' }).nth(1)).toHaveValue('Success: $2,000.00 deposited. Your new cash balance is $12,000.00.');
        await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$12,000.00');
        
        await page.getByRole('tab', { name: 'History' }).click();
        const firstHistoryRow = page.locator('.gr-table tr').nth(1);
        await expect(firstHistoryRow).toContainText('DEPOSIT');
        await expect(firstHistoryRow).toContainText('$2,000.00');
    });

    test('2.2 Successful Withdrawal and Balance Update', async ({ page }) => {
        await createAccount(page, 'cashTrader2', 'password123', 7000);
        await page.getByRole('tab', { name: 'Cash Management' }).click();

        await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$7,000.00');

        await page.getByLabel('Amount ($)').fill('1500');
        await page.getByRole('button', { name: 'Withdraw' }).click();
        
        await expect(page.getByLabel('Status').nth(1)).toHaveValue('Success: $1,500.00 withdrawn. Your new cash balance is $5,500.00.');
        await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$5,500.00');

        await page.getByRole('tab', { name: 'History' }).click();
        const firstHistoryRow = page.locator('.gr-table tr').nth(1);
        await expect(firstHistoryRow).toContainText('WITHDRAWAL');
        await expect(firstHistoryRow).toContainText('$1,500.00');
    });

    test('2.3 Attempt to Withdraw More Than Available Balance', async ({ page }) => {
        await createAccount(page, 'cashTrader3', 'password123', 1000);
        await page.getByRole('tab', { name: 'Cash Management' }).click();

        await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$1,000.00');

        await page.getByLabel('Amount ($)').fill('1500');
        await page.getByRole('button', { name: 'Withdraw' }).click();

        await expect(page.getByLabel('Status').nth(1)).toHaveValue('Error: Insufficient funds. You cannot withdraw more than your available cash balance of $1,000.00.');
        await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$1,000.00');
    });
    
    test('2.4 Attempt to Deposit/Withdraw an Invalid Amount', async ({ page }) => {
        await createAccount(page, 'cashTrader4', 'password123', 5000);
        await page.getByRole('tab', { name: 'Cash Management' }).click();

        await page.getByLabel('Amount ($)').fill('-50');
        
        await page.getByRole('button', { name: 'Deposit' }).click();
        await expect(page.getByLabel('Status').nth(1)).toHaveValue('Error: Amount must be a positive number.');
        
        await page.getByRole('button', { name: 'Withdraw' }).click();
        await expect(page.getByLabel('Status').nth(1)).toHaveValue('Error: Amount must be a positive number.');
        
        await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$5,000.00');
    });
});

test.describe('Epic 3: Trading and Execution', () => {

    test('3.1 Successful Share Purchase', async ({ page }) => {
        await createAccount(page, 'tradeExec1', 'password123', 10000);
        await page.getByRole('tab', { name: 'Trade' }).click();

        await page.locator('input[type="radio"]').nth(0).check(); // Select BUY
        await page.getByLabel('Stock Symbol').fill('AAPL');
        await page.getByLabel('Quantity').fill('10');
        await page.getByRole('button', { name: 'Execute Trade' }).click();

        await expect(page.getByLabel('Status').nth(2)).toHaveValue('Success: Bought 10 shares of AAPL at $150.00 each for a total of $1,500.00.');

        await page.getByRole('tab', { name: 'Portfolio' }).click();
        await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$8,500.00');
        const holdingsRow = page.locator('div[data-testid="dataframe"]').locator('tr').nth(1);
        await expect(holdingsRow.locator('td').nth(0)).toHaveText('AAPL');
        await expect(holdingsRow.locator('td').nth(1)).toHaveText('10');
        
        await page.getByRole('tab', { name: 'History' }).click();
        const historyRow = page.locator('.gr-table tr').nth(1);
        await expect(historyRow).toContainText('BUY');
        await expect(historyRow).toContainText('AAPL');
        await expect(historyRow).toContainText('10');
    });

    test('3.2 Successful Share Sale', async ({ page }) => {
        // Seeding step from 3.1
        await createAccount(page, 'tradeExec2', 'password123', 10000);
        await page.getByRole('tab', { name: 'Trade' }).click();
        await page.locator('input[type="radio"]').nth(0).check(); // BUY
        await page.getByLabel('Stock Symbol').fill('AAPL');
        await page.getByLabel('Quantity').fill('10');
        await page.getByRole('button', { name: 'Execute Trade' }).click();
        await expect(page.getByLabel('Status').nth(2)).toContainText('Success: Bought 10 shares of AAPL');

        // Main test steps
        await page.locator('input[type="radio"]').nth(1).check(); // Select SELL
        await page.getByLabel('Stock Symbol').fill('AAPL');
        await page.getByLabel('Quantity').fill('5');
        await page.getByRole('button', { name: 'Execute Trade' }).click();

        await expect(page.getByLabel('Status').nth(2)).toHaveValue('Success: Sold 5 shares of AAPL at $160.00 each for a total of $800.00.');
        
        await page.getByRole('tab', { name: 'Portfolio' }).click();
        await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$9,300.00');
        const holdingsRow = page.locator('div[data-testid="dataframe"]').locator('tr').nth(1);
        await expect(holdingsRow.locator('td').nth(0)).toHaveText('AAPL');
        await expect(holdingsRow.locator('td').nth(1)).toHaveText('5');

        await page.getByRole('tab', { name: 'History' }).click();
        const historyRow = page.locator('.gr-table tr').nth(1);
        await expect(historyRow).toContainText('SELL');
        await expect(historyRow).toContainText('AAPL');
        await expect(historyRow).toContainText('5');
    });
    
    test('3.3 Attempt to Buy with Insufficient Funds', async ({ page }) => {
        await createAccount(page, 'tradeExec3', 'password123', 1000);
        await page.getByRole('tab', { name: 'Trade' }).click();
        
        await page.locator('input[type="radio"]').nth(0).check(); // BUY
        await page.getByLabel('Stock Symbol').fill('TSLA');
        await page.getByLabel('Quantity').fill('4');
        await page.getByRole('button', { name: 'Execute Trade' }).click();

        await expect(page.getByLabel('Status').nth(2)).toHaveValue('Error: Insufficient funds. You need $1,200.00 to buy 4 shares of TSLA, but you only have $1,000.00.');
    });

    test('3.4 Attempt to Sell More Shares Than Owned', async ({ page }) => {
        // Seeding step
        await createAccount(page, 'tradeExec4', 'password123', 10000);
        await page.getByRole('tab', { name: 'Trade' }).click();
        await page.locator('input[type="radio"]').nth(0).check(); // BUY
        await page.getByLabel('Stock Symbol').fill('GOOGL');
        await page.getByLabel('Quantity').fill('5');
        await page.getByRole('button', { name: 'Execute Trade' }).click();
        await expect(page.getByLabel('Status').nth(2)).toContainText('Success: Bought 5 shares of GOOGL');
        
        // Main test step
        await page.locator('input[type="radio"]').nth(1).check(); // SELL
        await page.getByLabel('Stock Symbol').fill('GOOGL');
        await page.getByLabel('Quantity').fill('10');
        await page.getByRole('button', { name: 'Execute Trade' }).click();

        await expect(page.getByLabel('Status').nth(2)).toHaveValue('Error: Insufficient shares. You cannot sell 10 shares of GOOGL as you only own 5.');
    });

    test('3.5 Attempt to Trade an Invalid Symbol or Invalid Quantity', async ({ page }) => {
        await createAccount(page, 'tradeExec5', 'password123', 10000);
        await page.getByRole('tab', { name: 'Trade' }).click();
        
        // Invalid Symbol
        await page.locator('input[type="radio"]').nth(0).check(); // BUY
        await page.getByLabel('Stock Symbol').fill('XYZ');
        await page.getByLabel('Quantity').fill('1');
        await page.getByRole('button', { name: 'Execute Trade' }).click();
        await expect(page.getByLabel('Status').nth(2)).toHaveValue("Error: Invalid stock symbol 'XYZ'. Please use a valid symbol (e.g., AAPL, TSLA, GOOGL).");

        // Invalid Quantity (0)
        await page.getByLabel('Stock Symbol').fill('AAPL');
        await page.getByLabel('Quantity').fill('0');
        await page.getByRole('button', { name: 'Execute Trade' }).click();
        await expect(page.getByLabel('Status').nth(2)).toHaveValue("Error: Quantity must be a positive whole number.");

        // Invalid Quantity (-5)
        await page.getByLabel('Quantity').fill('-5');
        await page.getByRole('button', { name: 'Execute Trade' }).click();
        await expect(page.getByLabel('Status').nth(2)).toHaveValue("Error: Quantity must be a positive whole number.");
    });
});

test.describe('Epic 4: Portfolio and History Reporting', () => {

    test('4.1 Comprehensive End-to-End User Journey and Final Portfolio Verification', async ({ page }) => {
        // 1. Account Creation
        await createAccount(page, 'traderE2E', 'password123', 12000);

        // 2. Cash Management: Withdraw
        await page.getByRole('tab', { name: 'Cash Management' }).click();
        await page.getByLabel('Amount ($)').fill('2000');
        await page.getByRole('button', { name: 'Withdraw' }).click();
        await expect(page.getByLabel('Current Cash Balance')).toHaveValue('$10,000.00');

        // 3. First Purchase: AAPL
        await page.getByRole('tab', { name: 'Trade' }).click();
        await page.locator('input[type="radio"]').nth(0).check(); // BUY
        await page.getByLabel('Stock Symbol').fill('AAPL');
        await page.getByLabel('Quantity').fill('10');
        await page.getByRole('button', { name: 'Execute Trade' }).click();

        // 4. Second Purchase: TSLA
        await page.locator('input[type="radio"]').nth(0).check(); // BUY
        await page.getByLabel('Stock Symbol').fill('TSLA');
        await page.getByLabel('Quantity').fill('5');
        await page.getByRole('button', { name: 'Execute Trade' }).click();

        // 5. Portfolio Check
        await page.getByRole('tab', { name: 'Portfolio' }).click();
        await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$7,000.00');
        await expect(page.getByLabel('Total Portfolio Value ($)')).toHaveValue('$10,000.00');
        await expect(page.getByLabel('Total Profit / Loss ($)')).toHaveValue('$0.00');
        
        const holdingsTable = page.locator('div[data-testid="dataframe"]');
        await expect(holdingsTable.locator('tr:has-text("AAPL")').locator('td').nth(1)).toHaveText('10');
        await expect(holdingsTable.locator('tr:has-text("TSLA")').locator('td').nth(1)).toHaveText('5');

        // 6. History Check
        await page.getByRole('tab', { name: 'History' }).click();
        const historyTable = page.locator('.gr-table');
        const rows = await historyTable.locator('tr').all();
        expect(rows.length).toBe(5); // Header + 4 transactions

        await expect(rows[1]).toContainText('BUY');
        await expect(rows[1]).toContainText('TSLA');
        await expect(rows[1]).toContainText('5');
        await expect(rows[1]).toContainText('$1,500.00');

        await expect(rows[2]).toContainText('BUY');
        await expect(rows[2]).toContainText('AAPL');
        await expect(rows[2]).toContainText('10');
        await expect(rows[2]).toContainText('$1,500.00');

        await expect(rows[3]).toContainText('WITHDRAWAL');
        await expect(rows[3]).toContainText('$2,000.00');

        await expect(rows[4]).toContainText('DEPOSIT');
        await expect(rows[4]).toContainText('$12,000.00');
    });

    test('4.2 Verify Portfolio After Price Change and Refresh', async ({ page }) => {
        // Seeding steps from 4.1
        await createAccount(page, 'traderRefresh', 'password123', 12000);
        await page.getByRole('tab', { name: 'Cash Management' }).click();
        await page.getByLabel('Amount ($)').fill('2000');
        await page.getByRole('button', { name: 'Withdraw' }).click();
        await page.getByRole('tab', { name: 'Trade' }).click();
        await page.locator('input[type="radio"]').nth(0).check();
        await page.getByLabel('Stock Symbol').fill('AAPL');
        await page.getByLabel('Quantity').fill('10');
        await page.getByRole('button', { name: 'Execute Trade' }).click();
        await page.getByLabel('Stock Symbol').fill('TSLA');
        await page.getByLabel('Quantity').fill('5');
        await page.getByRole('button', { name: 'Execute Trade' }).click();

        // Navigate to Portfolio and click Refresh
        await page.getByRole('tab', { name: 'Portfolio' }).click();
        await page.getByRole('button', { name: 'Refresh' }).click();

        // Assertions based on assumed new prices (AAPL=$160, TSLA=$280)
        // These assertions assume the backend price service has been updated as per the test plan.
        await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$7,000.00');
        await expect(page.getByLabel('Total Portfolio Value ($)')).toHaveValue('$10,000.00'); // (10*160)+(5*280) + 7000 = 1600+1400+7000 = 10000
        await expect(page.getByLabel('Total Profit / Loss ($)')).toHaveValue('$0.00'); // 10000 portfolio - 10000 net deposit

        const holdingsTable = page.locator('div[data-testid="dataframe"]');
        const aaplRow = holdingsTable.locator('tr:has-text("AAPL")');
        await expect(aaplRow.locator('td').nth(2)).toHaveText('$160.00');
        await expect(aaplRow.locator('td').nth(3)).toHaveText('$1,600.00');

        const tslaRow = holdingsTable.locator('tr:has-text("TSLA")');
        await expect(tslaRow.locator('td').nth(2)).toHaveText('$280.00');
        await expect(tslaRow.locator('td').nth(3)).toHaveText('$1,400.00');
    });
});