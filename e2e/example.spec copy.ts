// spec: testplan.md

import { test, expect } from '@playwright/test';

// 1. Account Creation

test('Account Creation - Successful (Happy Path)', async ({ page }) => {
  await page.goto('http://127.0.0.1:7860');
  await page.getByLabel('Username').fill('trader123');
  await page.getByLabel('Password').fill('password123');
  await page.getByLabel('Initial Deposit Amount ($)').fill('10000');
  await page.getByRole('button', { name: 'Create Account' }).click();

  // Expect: Cash balance and portfolio value
  await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$10,000.00');
  await expect(page.getByLabel('Total Portfolio Value ($)')).toHaveValue('$10,000.00');
});

test('Account Creation - Non-Unique Username', async ({ page }) => {
  await page.goto('http://127.0.0.1:7860');
  await page.getByLabel('Username').fill('trader123');
  await page.getByLabel('Password').fill('password123');
  await page.getByLabel('Initial Deposit Amount ($)').fill('10000');
  await page.getByRole('button', { name: 'Create Account' }).click();

  // Expect: Error message about username taken
  await expect(page.locator('text=Username \'trader123\' is already taken')).toBeVisible();
});

test('Account Creation - Invalid Initial Deposit', async ({ page }) => {
  const deposits = ['0', '-100'];
  
  for (const deposit of deposits) {
    await page.goto('http://127.0.0.1:7860');
    await page.getByLabel('Username').fill(`newuser${deposit}`);
    await page.getByLabel('Password').fill('password123');
    await page.getByLabel('Initial Deposit Amount ($)').fill(deposit);
    await page.getByRole('button', { name: 'Create Account' }).click();
    
    // Wait for error message to appear
    await expect(page.locator('text=/Initial deposit must be a positive number/i')).toBeVisible({ timeout: 5000 });
  }
});

// 2. Cash Management

test('Cash Management - Successful Deposit', async ({ page }) => {
  // Assume user is logged in with $5,000 balance
  await page.getByRole('tab', { name: 'Cash Management' }).click();
  await page.getByLabel('Amount ($)').fill('2000');
  await page.getByRole('button', { name: 'Deposit' }).click();

  await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$7,000.00');
});

test('Cash Management - Successful Withdrawal', async ({ page }) => {
  await page.getByRole('tab', { name: 'Cash Management' }).click();
  await page.getByLabel('Amount ($)').fill('1500');
  await page.getByRole('button', { name: 'Withdraw' }).click();

  await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$5,500.00');
});

test('Cash Management - Withdraw More Than Available', async ({ page }) => {
  await page.getByRole('tab', { name: 'Cash Management' }).click();
  await page.getByLabel('Amount ($)').fill('1500');
  await page.getByRole('button', { name: 'Withdraw' }).click();

  await expect(page.locator('text=Insufficient funds')).toBeVisible();
});

test('Cash Management - Invalid Amount', async ({ page }) => {
  await page.getByRole('tab', { name: 'Cash Management' }).click();
  for (const amount of ['-50', '0']) {
    await page.getByLabel('Amount ($)').fill(amount);
    await page.getByRole('button', { name: 'Deposit' }).click();
    await expect(page.locator('text=Amount must be a positive number')).toBeVisible();
    await page.getByRole('button', { name: 'Withdraw' }).click();
    await expect(page.locator('text=Amount must be a positive number')).toBeVisible();
  }
});

// 3. Trade Execution

test('Trade Execution - Successful Buy', async ({ page }) => {
  await page.getByRole('tab', { name: 'Trade' }).click();
  await page.getByLabel('Action').selectOption('BUY');
  await page.getByLabel('Stock Symbol (e.g., AAPL)').fill('AAPL');
  await page.getByLabel('Quantity').fill('10');
  await page.getByRole('button', { name: 'Execute Trade' }).click();

  await expect(page.locator('text=Bought 10 shares of AAPL')).toBeVisible();
});

test('Trade Execution - Successful Sell', async ({ page }) => {
  await page.getByRole('tab', { name: 'Trade' }).click();
  await page.getByLabel('Action').selectOption('SELL');
  await page.getByLabel('Stock Symbol (e.g., AAPL)').fill('AAPL');
  await page.getByLabel('Quantity').fill('5');
  await page.getByRole('button', { name: 'Execute Trade' }).click();

  await expect(page.locator('text=Sold 5 shares of AAPL')).toBeVisible();
});

test('Trade Execution - Buy with Insufficient Funds', async ({ page }) => {
  await page.getByRole('tab', { name: 'Trade' }).click();
  await page.getByLabel('Action').selectOption('BUY');
  await page.getByLabel('Stock Symbol (e.g., TSLA)').fill('TSLA');
  await page.getByLabel('Quantity').fill('4');
  await page.getByRole('button', { name: 'Execute Trade' }).click();

  await expect(page.locator('text=Insufficient funds')).toBeVisible();
});

test('Trade Execution - Sell More Than Owned', async ({ page }) => {
  await page.getByRole('tab', { name: 'Trade' }).click();
  await page.getByLabel('Action').selectOption('SELL');
  await page.getByLabel('Stock Symbol (e.g., GOOGL)').fill('GOOGL');
  await page.getByLabel('Quantity').fill('10');
  await page.getByRole('button', { name: 'Execute Trade' }).click();

  await expect(page.locator('text=Insufficient shares')).toBeVisible();
});

test('Trade Execution - Invalid Symbol', async ({ page }) => {
  await page.getByRole('tab', { name: 'Trade' }).click();
  await page.getByLabel('Stock Symbol (e.g., AAPL)').fill('XYZ');
  await page.getByLabel('Quantity').fill('1');
  await page.getByRole('button', { name: 'Execute Trade' }).click();

  await expect(page.locator('text=Invalid stock symbol')).toBeVisible();
});

test('Trade Execution - Invalid Quantity', async ({ page }) => {
  await page.getByRole('tab', { name: 'Trade' }).click();
  for (const qty of ['0', '-5', '2.5']) {
    await page.getByLabel('Quantity').fill(qty);
    await page.getByRole('button', { name: 'Execute Trade' }).click();
    await expect(page.locator('text=Quantity must be a positive whole number')).toBeVisible();
  }
});

// 4. Portfolio & History

test('Portfolio - View Summary', async ({ page }) => {
  await page.getByRole('tab', { name: 'Portfolio' }).click();
  await page.getByRole('button', { name: 'Refresh' }).click();

  await expect(page.getByLabel('Total Portfolio Value ($)')).toHaveValue('$8,000.00');
  await expect(page.getByLabel('Cash Balance ($)')).toHaveValue('$5,000.00');
  await expect(page.getByLabel('Total Profit / Loss ($)')).toHaveValue('-$2,000.00');
});

test('History - View Transactions', async ({ page }) => {
  await page.getByRole('tab', { name: 'History' }).click();
  await expect(page.locator('text=DEPOSIT')).toBeVisible();
  await expect(page.locator('text=BUY')).toBeVisible();
  await expect(page.locator('text=SELL')).toBeVisible();
});

test('Portfolio/History - Empty State', async ({ page }) => {
  await page.getByRole('tab', { name: 'Portfolio' }).click();
  await expect(page.locator('text=No shares owned')).toBeVisible();
  await expect(page.getByLabel('Total Portfolio Value ($)')).toHaveValue('$10,000.00');
  await expect(page.getByLabel('Total Profit / Loss ($)')).toHaveValue('$0.00');

  await page.getByRole('tab', { name: 'History' }).click();
  await expect(page.locator('text=DEPOSIT')).toBeVisible();
});