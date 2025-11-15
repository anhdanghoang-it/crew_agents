# Trading Simulation Platform - Comprehensive Test Plan

## Application Overview

The Trading Simulation Platform is a Gradio-based web application that provides users with a realistic stock trading simulation environment. The platform enables users to manage virtual trading accounts, execute buy/sell transactions, manage cash balances, and track portfolio performance over time.

### Core Features
- **Account Creation**: Users can create new accounts with initial capital deposits
- **Cash Management**: Deposit and withdraw funds from trading accounts
- **Stock Trading**: Buy and sell shares of stocks (AAPL, TSLA, GOOGL) with real-time pricing
- **Portfolio Tracking**: View current holdings, total portfolio value, and profit/loss calculations
- **Transaction History**: Complete audit trail of all account activities

### Technical Stack
- **Frontend**: Gradio web interface with tabbed navigation
- **Pricing**: External `get_share_price()` API for stock prices
- **Data Storage**: User accounts, transactions, and holdings persistence

---

## Test Environment Setup

**Seed File**: `tests/seed.spec.ts`

### Prerequisites
- Application running at `http://127.0.0.1:7860`
- Test account creation:
  - Username: `trader123`
  - Password: `password123`
  - Initial deposit: `$10,000`

### Supported Stock Symbols
- AAPL (Apple Inc.)
- TSLA (Tesla Inc.)
- GOOGL (Alphabet Inc.)

---

## Test Scenarios

### Epic 1: Account Management (US-001)

#### 1.1 Create New Account with Valid Initial Deposit

**Priority**: Critical  
**User Story**: US-001  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to `http://127.0.0.1:7860`
2. Locate the "Username" textbox
3. Enter username: `trader123`
4. Locate the "Password" textbox (password type)
5. Enter password: `password123`
6. Locate the "Initial Deposit Amount ($)" number input
7. Enter amount: `10000`
8. Click the "Create Account" button
9. Navigate to the "Portfolio" tab

**Expected Results:**
- Status message displays: "Success: Account 'trader123' created with an initial deposit of $10,000.00."
- Cash Balance shows: `$10,000.00`
- Total Portfolio Value shows: `$10,000.00`
- Total Profit / Loss shows: `$0.00`
- Current Holdings table is empty (no shares owned)
- Transaction History shows one DEPOSIT entry for $10,000.00

---

#### 1.2 Attempt to Create Duplicate Account

**Priority**: High  
**User Story**: US-001 (AC-2)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to `http://127.0.0.1:7860`
2. Enter username: `trader123` (existing user from seed)
3. Enter password: `newpassword456`
4. Enter initial deposit: `5000`
5. Click the "Create Account" button

**Expected Results:**
- Account creation is rejected
- Status displays error: "Error: Username 'trader123' is already taken. Please choose a different username."
- No new account is created
- Existing account data remains unchanged

---

#### 1.3 Create Account with Invalid Initial Deposit - Non-Numeric

**Priority**: High  
**User Story**: US-001 (AC-3)  
**Seed**: None (fresh state)

**Steps:**
1. Navigate to `http://127.0.0.1:7860`
2. Enter username: `testuser1`
3. Enter password: `password123`
4. Locate the "Initial Deposit Amount ($)" field
5. Attempt to enter: `abc` (non-numeric value)
6. Click the "Create Account" button

**Expected Results:**
- Input field validation prevents non-numeric entry OR
- Status displays error: "Error: Initial deposit must be a positive number."
- No account is created

---

#### 1.4 Create Account with Zero Initial Deposit

**Priority**: High  
**User Story**: US-001 (AC-3)  
**Seed**: None (fresh state)

**Steps:**
1. Navigate to `http://127.0.0.1:7860`
2. Enter username: `testuser2`
3. Enter password: `password123`
4. Enter initial deposit: `0`
5. Click the "Create Account" button

**Expected Results:**
- Account creation is rejected
- Status displays error: "Error: Initial deposit must be a positive number."
- No account is created

---

#### 1.5 Create Account with Negative Initial Deposit

**Priority**: High  
**User Story**: US-001 (AC-3)  
**Seed**: None (fresh state)

**Steps:**
1. Navigate to `http://127.0.0.1:7860`
2. Enter username: `testuser3`
3. Enter password: `password123`
4. Enter initial deposit: `-100`
5. Click the "Create Account" button

**Expected Results:**
- Account creation is rejected
- Status displays error: "Error: Initial deposit must be a positive number."
- No account is created

---

#### 1.6 Create Account with Large Initial Deposit

**Priority**: Medium  
**User Story**: US-001  
**Seed**: None (fresh state)

**Steps:**
1. Navigate to `http://127.0.0.1:7860`
2. Enter username: `wealthytrader`
3. Enter password: `password123`
4. Enter initial deposit: `1000000` (one million)
5. Click the "Create Account" button
6. Navigate to "Portfolio" tab

**Expected Results:**
- Status displays: "Success: Account 'wealthytrader' created with an initial deposit of $1,000,000.00."
- Cash Balance shows: `$1,000,000.00`
- Total Portfolio Value shows: `$1,000,000.00`
- System handles large numbers correctly without overflow

---

### Epic 2: Cash Management (US-002)

#### 2.1 Deposit Funds to Account

**Priority**: High  
**User Story**: US-002 (AC-1)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application (user logged in with $10,000 balance)
2. Click the "Cash Management" tab
3. Verify "Current Cash Balance" displays: `$10,000.00`
4. Locate the "Amount ($)" number input
5. Enter amount: `2000`
6. Click the "Deposit" button
7. Navigate to "Portfolio" tab to verify

**Expected Results:**
- Status displays: "Success: $2,000.00 deposited. Your new cash balance is $12,000.00."
- Current Cash Balance updates to: `$12,000.00`
- Portfolio tab shows Cash Balance: `$12,000.00`
- Total Portfolio Value increases to: `$12,000.00`
- Transaction History shows new DEPOSIT entry for $2,000.00

---

#### 2.2 Withdraw Funds from Account

**Priority**: High  
**User Story**: US-002 (AC-2)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application (user logged in with $10,000 balance)
2. Click the "Cash Management" tab
3. Enter amount: `1500`
4. Click the "Withdraw" button
5. Navigate to "Portfolio" tab to verify

**Expected Results:**
- Status displays: "Success: $1,500.00 withdrawn. Your new cash balance is $8,500.00."
- Current Cash Balance updates to: `$8,500.00`
- Portfolio tab shows Cash Balance: `$8,500.00`
- Total Portfolio Value decreases to: `$8,500.00`
- Transaction History shows new WITHDRAWAL entry for $1,500.00

---

#### 2.3 Attempt to Withdraw More Than Available Balance

**Priority**: High  
**User Story**: US-002 (AC-3)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application (user logged in with $10,000 balance)
2. Click the "Cash Management" tab
3. Verify Current Cash Balance: `$10,000.00`
4. Enter amount: `15000` (more than available)
5. Click the "Withdraw" button

**Expected Results:**
- Withdrawal is rejected
- Status displays: "Error: Insufficient funds. You cannot withdraw more than your available cash balance of $10,000.00."
- Cash balance remains: `$10,000.00`
- No transaction is recorded in history

---

#### 2.4 Attempt to Deposit Negative Amount

**Priority**: High  
**User Story**: US-002 (AC-4)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application
2. Click the "Cash Management" tab
3. Enter amount: `-50`
4. Click the "Deposit" button

**Expected Results:**
- Input field validation prevents negative entry OR
- Status displays: "Error: Amount must be a positive number."
- Cash balance remains unchanged
- No transaction is recorded

---

#### 2.5 Attempt to Withdraw Negative Amount

**Priority**: High  
**User Story**: US-002 (AC-4)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application
2. Click the "Cash Management" tab
3. Enter amount: `-100`
4. Click the "Withdraw" button

**Expected Results:**
- Input field validation prevents negative entry OR
- Status displays: "Error: Amount must be a positive number."
- Cash balance remains unchanged
- No transaction is recorded

---

#### 2.6 Attempt to Deposit/Withdraw Zero Amount

**Priority**: Medium  
**User Story**: US-002 (AC-4)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application
2. Click the "Cash Management" tab
3. Enter amount: `0`
4. Click the "Deposit" button
5. Verify error message
6. Click the "Withdraw" button

**Expected Results:**
- Both operations are rejected
- Status displays: "Error: Amount must be a positive number."
- Cash balance remains unchanged
- No transactions are recorded

---

#### 2.7 Multiple Sequential Deposits and Withdrawals

**Priority**: Medium  
**User Story**: US-002  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application (starting balance: $10,000)
2. Click "Cash Management" tab
3. Deposit $5,000 (new balance should be $15,000)
4. Withdraw $2,000 (new balance should be $13,000)
5. Deposit $3,000 (new balance should be $16,000)
6. Withdraw $1,000 (new balance should be $15,000)
7. Navigate to "History" tab

**Expected Results:**
- Final Cash Balance: `$15,000.00`
- Total Portfolio Value: `$15,000.00`
- Net Deposits calculation: `$10,000 (initial) + $5,000 + $3,000 - $2,000 - $1,000 = $15,000`
- Transaction History shows all 5 transactions in reverse chronological order
- Total Profit/Loss: `$0.00` (since portfolio value equals net deposits)

---

### Epic 3: Stock Trading (US-003)

#### 3.1 Buy Shares - Successful Purchase

**Priority**: Critical  
**User Story**: US-003 (AC-1)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application (cash balance: $10,000)
2. Click the "Trade" tab
3. Verify "Action" dropdown is set to: `BUY`
4. Enter "Stock Symbol": `AAPL`
5. Enter "Quantity": `10`
6. Click "Execute Trade" button
7. Navigate to "Portfolio" tab
8. Click "Refresh" button to update prices

**Expected Results:**
- Status displays: "Success: Bought 10 shares of AAPL at $150.00 each for a total of $1,500.00."
- Cash Balance reduces to: `$8,500.00` ($10,000 - $1,500)
- Current Holdings table shows:
  - Symbol: `AAPL`
  - Quantity: `10`
  - Current Price: `$150.00`
  - Total Value: `$1,500.00`
- Total Portfolio Value: `$10,000.00` ($8,500 cash + $1,500 shares)
- Transaction History shows new BUY entry with all details

---

#### 3.2 Sell Shares - Successful Sale

**Priority**: Critical  
**User Story**: US-003 (AC-2)  
**Seed**: Custom (account with AAPL shares)

**Prerequisites:**
- Account has 10 shares of AAPL
- Cash balance: $8,500

**Steps:**
1. Navigate to application
2. Click the "Trade" tab
3. Select "Action": `SELL` from dropdown
4. Enter "Stock Symbol": `AAPL`
5. Enter "Quantity": `5`
6. Click "Execute Trade" button
7. Navigate to "Portfolio" tab
8. Click "Refresh" button

**Expected Results:**
- Status displays: "Success: Sold 5 shares of AAPL at $150.00 each for a total of $750.00."
- Cash Balance increases to: `$9,250.00` ($8,500 + $750)
- Current Holdings shows:
  - AAPL Quantity: `5` (reduced from 10)
  - Total Value: `$750.00`
- Transaction History shows new SELL entry

---

#### 3.3 Buy Multiple Different Stocks

**Priority**: High  
**User Story**: US-003  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application (cash balance: $10,000)
2. Click "Trade" tab
3. Buy 10 shares of AAPL (cost: $1,500)
4. Buy 5 shares of TSLA at $300 each (cost: $1,500)
5. Buy 2 shares of GOOGL at $140 each (cost: $280)
6. Navigate to "Portfolio" tab
7. Click "Refresh" button

**Expected Results:**
- Cash Balance: `$6,720.00` ($10,000 - $1,500 - $1,500 - $280)
- Current Holdings shows three rows:
  - AAPL: 10 shares, $150 each, $1,500 total
  - TSLA: 5 shares, $300 each, $1,500 total
  - GOOGL: 2 shares, $140 each, $280 total
- Total Portfolio Value: `$10,000.00`
- Transaction History shows all three BUY transactions

---

#### 3.4 Attempt to Buy with Insufficient Funds

**Priority**: Critical  
**User Story**: US-003 (AC-3)  
**Seed**: Custom (account with $1,000 balance)

**Steps:**
1. Navigate to application (cash balance: $1,000)
2. Click "Trade" tab
3. Select Action: `BUY`
4. Enter Stock Symbol: `TSLA`
5. Enter Quantity: `4` (cost would be $1,200 at $300 per share)
6. Click "Execute Trade" button

**Expected Results:**
- Transaction is rejected
- Status displays: "Error: Insufficient funds. You need $1,200.00 to buy 4 shares of TSLA, but you only have $1,000.00."
- Cash balance remains: `$1,000.00`
- No shares are added to holdings
- No transaction is recorded in history

---

#### 3.5 Attempt to Sell More Shares Than Owned

**Priority**: Critical  
**User Story**: US-003 (AC-4)  
**Seed**: Custom (account with 5 shares of GOOGL)

**Steps:**
1. Navigate to application (owns 5 shares of GOOGL)
2. Navigate to "Portfolio" tab to verify holdings
3. Click "Trade" tab
4. Select Action: `SELL`
5. Enter Stock Symbol: `GOOGL`
6. Enter Quantity: `10`
7. Click "Execute Trade" button

**Expected Results:**
- Transaction is rejected
- Status displays: "Error: Insufficient shares. You cannot sell 10 shares of GOOGL as you only own 5."
- Holdings remain: 5 shares of GOOGL
- Cash balance remains unchanged
- No transaction is recorded

---

#### 3.6 Attempt to Trade with Invalid Stock Symbol

**Priority**: High  
**User Story**: US-003 (AC-5)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application
2. Click "Trade" tab
3. Select Action: `BUY`
4. Enter Stock Symbol: `XYZ` (invalid symbol)
5. Enter Quantity: `10`
6. Click "Execute Trade" button

**Expected Results:**
- Transaction is rejected
- Status displays: "Error: Invalid stock symbol 'XYZ'. Please use a valid symbol (e.g., AAPL, TSLA, GOOGL)."
- Cash balance remains unchanged
- No shares are added
- No transaction is recorded

---

#### 3.7 Attempt to Buy Zero Shares

**Priority**: Medium  
**User Story**: US-003 (AC-6)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application
2. Click "Trade" tab
3. Enter Stock Symbol: `AAPL`
4. Enter Quantity: `0`
5. Click "Execute Trade" button

**Expected Results:**
- Transaction is rejected
- Status displays: "Error: Quantity must be a positive whole number."
- No transaction occurs
- Cash and holdings remain unchanged

---

#### 3.8 Attempt to Buy Negative Shares

**Priority**: Medium  
**User Story**: US-003 (AC-6)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application
2. Click "Trade" tab
3. Enter Stock Symbol: `TSLA`
4. Attempt to enter Quantity: `-5`
5. Click "Execute Trade" button

**Expected Results:**
- Input field validation prevents negative entry OR
- Status displays: "Error: Quantity must be a positive whole number."
- No transaction occurs

---

#### 3.9 Attempt to Buy Fractional Shares

**Priority**: Medium  
**User Story**: US-003 (AC-6)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application
2. Click "Trade" tab
3. Enter Stock Symbol: `AAPL`
4. Attempt to enter Quantity: `2.5` (fractional)
5. Click "Execute Trade" button

**Expected Results:**
- Input field validation prevents decimal entry (precision=0) OR
- Status displays: "Error: Quantity must be a positive whole number."
- No transaction occurs

---

#### 3.10 Sell All Shares of a Stock

**Priority**: Medium  
**User Story**: US-003  
**Seed**: Custom (owns 10 shares of AAPL)

**Steps:**
1. Navigate to application (owns 10 shares of AAPL)
2. Click "Trade" tab
3. Select Action: `SELL`
4. Enter Stock Symbol: `AAPL`
5. Enter Quantity: `10` (all owned shares)
6. Click "Execute Trade" button
7. Navigate to "Portfolio" tab

**Expected Results:**
- Status displays successful sale message
- Cash balance increases by sale proceeds
- AAPL is removed from Current Holdings table (or shows 0 quantity)
- Transaction History shows SELL transaction

---

#### 3.11 Attempt to Sell Stock Not Owned

**Priority**: Medium  
**User Story**: US-003  
**Seed**: `tests/seed.spec.ts` (no shares owned)

**Steps:**
1. Navigate to application (no shares in portfolio)
2. Click "Trade" tab
3. Select Action: `SELL`
4. Enter Stock Symbol: `AAPL`
5. Enter Quantity: `5`
6. Click "Execute Trade" button

**Expected Results:**
- Transaction is rejected
- Status displays: "Error: Insufficient shares. You cannot sell 5 shares of AAPL as you only own 0."
- No transaction occurs
- Cash balance remains unchanged

---

#### 3.12 Trading with Empty Stock Symbol

**Priority**: Medium  
**User Story**: US-003  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application
2. Click "Trade" tab
3. Leave "Stock Symbol" field empty
4. Enter Quantity: `10`
5. Click "Execute Trade" button

**Expected Results:**
- Transaction is rejected
- Appropriate error message is displayed
- No transaction occurs

---

### Epic 4: Portfolio and History Viewing (US-004)

#### 4.1 View Portfolio with Correct Calculations

**Priority**: Critical  
**User Story**: US-004 (AC-1)  
**Seed**: Custom

**Prerequisites:**
- Total deposits: $12,000
- Total withdrawals: $2,000
- Net deposits: $10,000
- Cash balance: $5,000
- Holdings: 10 shares AAPL ($150 each), 5 shares TSLA ($300 each)

**Steps:**
1. Navigate to application
2. Click "Portfolio" tab
3. Click "Refresh" button to get latest prices
4. Verify all displayed values

**Expected Results:**
- Cash Balance: `$5,000.00`
- Current Holdings table shows:
  - AAPL: 10 shares @ $150.00 = $1,500.00
  - TSLA: 5 shares @ $300.00 = $1,500.00
- Total Value of Shares: `$3,000.00` ($1,500 + $1,500)
- Total Portfolio Value: `$8,000.00` ($5,000 cash + $3,000 shares)
- Total Profit/Loss: `-$2,000.00` ($8,000 portfolio - $10,000 net deposits)

---

#### 4.2 Portfolio Refresh Updates Prices

**Priority**: High  
**User Story**: US-004  
**Seed**: Custom (owns shares)

**Steps:**
1. Navigate to application (owns AAPL shares)
2. Click "Portfolio" tab
3. Note current price and total value of AAPL
4. Click "Refresh" button
5. Observe if prices update (assuming price API returns different values)

**Expected Results:**
- "Refresh" button triggers price update via `get_share_price()` API
- Current Price column updates to latest values
- Total Value recalculates based on new prices
- Total Portfolio Value recalculates
- Profit/Loss recalculates based on new portfolio value

---

#### 4.3 View Transaction History - Complete Audit Trail

**Priority**: High  
**User Story**: US-004 (AC-2)  
**Seed**: Custom

**Prerequisites:**
- Account has made multiple transactions:
  1. Initial deposit: $10,000
  2. Bought 10 AAPL
  3. Deposited $2,000
  4. Sold 5 GOOGL
  5. Withdrew $500

**Steps:**
1. Navigate to application
2. Click "History" tab
3. Examine the transaction history table

**Expected Results:**
- History displays all 5 transactions
- Transactions are in reverse chronological order (most recent first)
- Each entry includes:
  - Timestamp (date and time)
  - Type (DEPOSIT, WITHDRAWAL, BUY, SELL)
  - Symbol (for BUY/SELL, "null" for DEPOSIT/WITHDRAWAL)
  - Quantity (for BUY/SELL, "null" otherwise)
  - Price (per share for BUY/SELL, "N/A" otherwise)
  - Total (dollar amount)
- All amounts are formatted correctly with currency symbols

---

#### 4.4 View Empty Portfolio - New Account

**Priority**: Medium  
**User Story**: US-004 (AC-3)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Create new account with $10,000 initial deposit
2. Navigate to "Portfolio" tab (make no trades)

**Expected Results:**
- Cash Balance: `$10,000.00`
- Current Holdings table is empty or shows message "You do not own any shares."
- Total Portfolio Value: `$10,000.00` (equals cash balance)
- Total Profit/Loss: `$0.00`
- History tab shows only one transaction: initial DEPOSIT for $10,000

---

#### 4.5 View Portfolio with Only Cash (No Holdings)

**Priority**: Medium  
**User Story**: US-004  
**Seed**: Custom

**Prerequisites:**
- User deposited and withdrew funds but never bought shares
- Cash balance: $7,500
- Net deposits: $7,500

**Steps:**
1. Navigate to application
2. Click "Portfolio" tab

**Expected Results:**
- Cash Balance: `$7,500.00`
- Current Holdings shows no shares
- Total Portfolio Value: `$7,500.00`
- Total Profit/Loss: `$0.00`

---

#### 4.6 View Portfolio with Multiple Holdings

**Priority**: High  
**User Story**: US-004  
**Seed**: Custom (owns AAPL, TSLA, GOOGL)

**Steps:**
1. Navigate to application (owns shares of 3 different stocks)
2. Click "Portfolio" tab
3. Click "Refresh" button

**Expected Results:**
- Current Holdings table displays all 3 stocks in separate rows
- Each row shows correct Symbol, Quantity, Current Price, Total Value
- Total Portfolio Value correctly sums cash + all share values
- All monetary values formatted correctly

---

#### 4.7 Transaction History with Large Number of Entries

**Priority**: Medium  
**User Story**: US-004 (NFR)  
**Seed**: Custom (account with 100+ transactions)

**Steps:**
1. Create account with extensive trading history (100+ transactions)
2. Click "History" tab
3. Scroll through transaction history
4. Verify UI performance

**Expected Results:**
- All transactions are displayed correctly
- Table handles 100+ rows without significant lag (< 2 seconds load)
- Scrolling is smooth
- All data is accurately formatted
- Timestamps maintain reverse chronological order

---

#### 4.8 Verify Profit/Loss After Profitable Trade

**Priority**: High  
**User Story**: US-004  
**Seed**: Custom

**Scenario Setup:**
1. Initial deposit: $10,000 (net deposits = $10,000)
2. Buy 10 AAPL at $150 each (cost: $1,500, cash: $8,500)
3. Price increases to $160 per share

**Steps:**
1. Navigate to "Portfolio" tab
2. Click "Refresh" button to get updated prices
3. Verify Profit/Loss calculation

**Expected Results:**
- Cash Balance: `$8,500.00`
- AAPL holdings: 10 shares @ $160.00 = $1,600.00
- Total Portfolio Value: `$10,100.00` ($8,500 + $1,600)
- Total Profit/Loss: `$100.00` ($10,100 - $10,000 net deposits)
- Profit/Loss displayed in appropriate format (positive value)

---

#### 4.9 Verify Profit/Loss After Loss-Making Trade

**Priority**: High  
**User Story**: US-004  
**Seed**: Custom

**Scenario Setup:**
1. Initial deposit: $10,000 (net deposits = $10,000)
2. Buy 10 TSLA at $300 each (cost: $3,000, cash: $7,000)
3. Price decreases to $280 per share

**Steps:**
1. Navigate to "Portfolio" tab
2. Click "Refresh" button
3. Verify Profit/Loss calculation

**Expected Results:**
- Cash Balance: `$7,000.00`
- TSLA holdings: 10 shares @ $280.00 = $2,800.00
- Total Portfolio Value: `$9,800.00` ($7,000 + $2,800)
- Total Profit/Loss: `-$200.00` ($9,800 - $10,000 net deposits)
- Loss displayed with negative sign or appropriate formatting

---

#### 4.10 Net Deposits Calculation with Multiple Cash Transactions

**Priority**: High  
**User Story**: US-004  
**Seed**: Custom

**Scenario Setup:**
1. Initial deposit: $10,000
2. Additional deposit: $5,000
3. Withdrawal: $2,000
4. Additional deposit: $3,000
5. Withdrawal: $1,000

**Steps:**
1. Perform all cash transactions above
2. Buy shares to reduce cash (e.g., 20 AAPL at $150 = $3,000)
3. Navigate to "Portfolio" tab
4. Verify calculations

**Expected Results:**
- Net Deposits calculation: $10,000 + $5,000 - $2,000 + $3,000 - $1,000 = $15,000
- Cash Balance: $12,000 (after $3,000 spent on shares)
- Share Value: $3,000
- Total Portfolio Value: $15,000
- Profit/Loss: $0.00 (portfolio value equals net deposits)

---

### Epic 5: Integration and End-to-End Scenarios

#### 5.1 Complete User Journey - Account Creation to First Trade

**Priority**: Critical  
**Seed**: None (fresh state)

**Steps:**
1. Navigate to `http://127.0.0.1:7860`
2. Create account: `newtrader`, password, $15,000 initial deposit
3. Verify Portfolio shows $15,000 cash, $0 P/L
4. Navigate to "Trade" tab
5. Buy 20 shares of AAPL
6. Verify success message with price and total
7. Navigate to "Portfolio" tab
8. Click "Refresh" button
9. Verify holdings show 20 AAPL shares
10. Verify cash reduced by purchase amount
11. Navigate to "History" tab
12. Verify both DEPOSIT and BUY transactions appear

**Expected Results:**
- All steps complete successfully
- Data consistency across all tabs
- Correct calculations throughout
- No errors or unexpected behavior

---

#### 5.2 Complex Trading Scenario - Multiple Buy/Sell Operations

**Priority**: High  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Starting balance: $10,000
2. Buy 10 AAPL at $150 (cost: $1,500, remaining: $8,500)
3. Buy 5 TSLA at $300 (cost: $1,500, remaining: $7,000)
4. Sell 5 AAPL at $150 (gain: $750, remaining: $7,750)
5. Deposit $5,000 (new balance: $12,750)
6. Buy 3 GOOGL at $140 (cost: $420, remaining: $12,330)
7. Withdraw $2,000 (new balance: $10,330)
8. Sell all TSLA at $300 (gain: $1,500, remaining: $11,830)

**Expected Results:**
- Final Cash Balance: $11,830
- Holdings:
  - AAPL: 5 shares
  - GOOGL: 3 shares
- Net Deposits: $10,000 + $5,000 - $2,000 = $13,000
- All transactions appear in History
- Portfolio calculations are accurate
- No data inconsistencies

---

#### 5.3 Cash Management with Trading Integration

**Priority**: High  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Starting: $10,000
2. Buy stocks until low cash (e.g., $500 remaining)
3. Attempt to buy more expensive stock
4. Verify insufficient funds error
5. Deposit additional cash ($5,000)
6. Retry the same purchase
7. Verify success

**Expected Results:**
- First purchase fails with clear error message
- After deposit, sufficient funds available
- Second purchase succeeds
- Cash balance correctly reflects all transactions

---

#### 5.4 Refresh Functionality Across All Tabs

**Priority**: Medium  
**Seed**: Custom (owns shares)

**Steps:**
1. Navigate to "Portfolio" tab
2. Note current prices and values
3. Click "Refresh" button
4. Navigate to "Cash Management" tab
5. Verify cash balance consistency
6. Navigate to "Trade" tab
7. Execute a trade
8. Return to "Portfolio" tab
9. Verify holdings updated without manual refresh

**Expected Results:**
- Refresh button updates prices from `get_share_price()` API
- Data remains consistent across all tabs
- UI updates reflect latest state
- No stale data displayed

---

#### 5.5 API Price Retrieval Failure Handling

**Priority**: High  
**User Story**: US-003 (NFR)  
**Seed**: `tests/seed.spec.ts`

**Prerequisites:**
- Simulate `get_share_price()` API failure (mock/intercept network)

**Steps:**
1. Navigate to "Trade" tab
2. Attempt to buy shares of AAPL
3. Trigger API failure scenario
4. Click "Execute Trade" button

**Expected Results:**
- System gracefully handles API failure
- Status displays user-friendly error: "Error: Could not retrieve share price. Please try again later."
- No transaction occurs
- Cash and holdings remain unchanged
- Application remains stable (no crashes)

---

#### 5.6 Concurrent Operations - Rapid Actions

**Priority**: Medium  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to "Cash Management" tab
2. Quickly deposit $1,000
3. Immediately click "Trade" tab
4. Quickly execute a buy order
5. Verify both operations complete correctly

**Expected Results:**
- Both operations process successfully
- No race conditions or data corruption
- Final state reflects both transactions
- UI updates appropriately

---

#### 5.7 Boundary Testing - Maximum Allowed Values

**Priority**: Medium  
**Seed**: Custom

**Steps:**
1. Create account with very large initial deposit (e.g., $999,999,999)
2. Buy maximum possible shares
3. Verify system handles large numbers
4. Check Portfolio calculations with large values
5. Perform operations near integer/float boundaries

**Expected Results:**
- System handles large monetary values correctly
- No overflow errors
- Currency formatting remains correct
- Calculations are accurate
- No precision loss in profit/loss calculations

---

### Epic 6: UI/UX and Accessibility

#### 6.1 Keyboard Navigation - Complete Workflow

**Priority**: Medium  
**Accessibility**: Critical  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to application
2. Use only keyboard (Tab, Enter, Arrow keys)
3. Navigate through all tabs using Tab key
4. Fill in form fields using keyboard only
5. Execute trades using Enter key
6. Verify all interactive elements are reachable

**Expected Results:**
- All tabs are keyboard accessible
- All form inputs can be filled via keyboard
- All buttons can be activated with Enter key
- Tab order is logical and intuitive
- Focus indicators are visible
- No keyboard traps

---

#### 6.2 Screen Reader Compatibility

**Priority**: Medium  
**Accessibility**: Critical  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Enable screen reader (e.g., NVDA, JAWS)
2. Navigate through all tabs
3. Listen to announcements for labels and values
4. Execute form submissions
5. Listen to status message announcements

**Expected Results:**
- All form labels are read correctly
- Status messages are announced
- Data tables are navigable and readable
- All buttons have descriptive text
- Values are read with appropriate context

---

#### 6.3 Responsive Layout - Different Viewport Sizes

**Priority**: Low  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Open application in desktop browser (1920x1080)
2. Verify layout and all elements visible
3. Resize to tablet size (768x1024)
4. Verify layout adjusts appropriately
5. Resize to mobile size (375x667)
6. Test all functionality at each size

**Expected Results:**
- Layout adapts to different screen sizes
- All elements remain accessible and usable
- No horizontal scrolling required
- Touch targets are appropriately sized on mobile
- All functionality works at all sizes

---

#### 6.4 Status Message Visibility and Clarity

**Priority**: High  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Perform various operations (deposits, trades, etc.)
2. Read all status messages
3. Verify messages appear promptly
4. Verify messages are clear and actionable

**Expected Results:**
- Success messages clearly indicate what happened
- Error messages clearly explain the problem
- Messages appear within 500ms of action
- Messages remain visible long enough to read
- Messages are color-coded appropriately (if applicable)

---

### Epic 7: Performance and Non-Functional Requirements

#### 7.1 Account Creation Performance

**Priority**: Medium  
**NFR**: Performance (US-001)  
**Seed**: None

**Steps:**
1. Note timestamp before creating account
2. Create account with valid data
3. Measure time until success message appears
4. Repeat 10 times and average

**Expected Results:**
- Account creation completes within 500ms
- UI feedback appears promptly
- No noticeable lag or delay
- Consistent performance across multiple attempts

---

#### 7.2 Cash Transaction Performance

**Priority**: Medium  
**NFR**: Performance (US-002)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to "Cash Management" tab
2. Measure time to complete deposit
3. Measure time to complete withdrawal
4. Repeat multiple times

**Expected Results:**
- Deposit operations complete within 300ms
- Withdrawal operations complete within 300ms
- UI updates immediately
- Consistent performance

---

#### 7.3 Trade Execution Performance

**Priority**: High  
**NFR**: Performance (US-003)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Navigate to "Trade" tab
2. Enter trade details
3. Measure time from clicking "Execute Trade" to status message
4. Include time for `get_share_price()` API call
5. Repeat for multiple stocks

**Expected Results:**
- Complete trade execution within 1 second
- Includes API call to get share price
- UI remains responsive during operation
- No freezing or blocking

---

#### 7.4 Portfolio Refresh Performance

**Priority**: Medium  
**NFR**: Performance (US-004)  
**Seed**: Custom (owns multiple stocks)

**Steps:**
1. Create portfolio with 5 different stocks
2. Navigate to "Portfolio" tab
3. Click "Refresh" button
4. Measure time until all prices update

**Expected Results:**
- Portfolio calculations complete within 1 second
- Multiple API calls (5 stocks) complete efficiently
- UI updates smoothly
- No lag when displaying updated values

---

#### 7.5 Transaction History Load Performance

**Priority**: Medium  
**NFR**: Scalability (US-004)  
**Seed**: Custom (1000+ transactions)

**Steps:**
1. Create account with 1000+ transactions
2. Navigate to "History" tab
3. Measure load time
4. Test scrolling performance
5. Verify all data loads correctly

**Expected Results:**
- History loads without significant lag
- Handles 1000+ transactions efficiently
- Scrolling remains smooth
- No UI freezing or errors
- All transaction data displays correctly

---

#### 7.6 Data Integrity - Atomic Transactions

**Priority**: Critical  
**NFR**: Data Integrity (US-002)  
**Seed**: `tests/seed.spec.ts`

**Steps:**
1. Simulate interruption during deposit operation
2. Verify either full success or full rollback
3. Check for partial state updates
4. Verify transaction history accuracy

**Expected Results:**
- No partial transactions
- Cash balance is always accurate
- Transaction history reflects actual state
- No orphaned or incomplete records
- System maintains consistency

---

## Test Data Requirements

### Valid Stock Symbols and Prices
- **AAPL**: $150.00
- **TSLA**: $300.00
- **GOOGL**: $140.00

### Test User Accounts
- **trader123**: Standard test account from seed
- **wealthytrader**: High-balance account ($1,000,000+)
- **lowcashtrader**: Low-balance account for insufficient funds testing

### Edge Case Values
- **Minimum deposit**: $0.01
- **Large deposit**: $999,999,999
- **Typical deposit**: $10,000
- **Maximum shares**: Test with 1000+ shares

---

## Glossary of Terms

### Net Deposits
The total amount of money deposited by the user minus the total amount of money withdrawn.
- **Formula**: `Sum(All DEPOSIT Transactions) - Sum(All WITHDRAWAL Transactions)`

### Total Portfolio Value
The current total worth of the user's account, including both cash and the current market value of all shares.
- **Formula**: `Current Cash Balance + Sum(Quantity of each share * Current Price of each share)`

### Profit / Loss (P/L)
The overall gain or loss of the account relative to the user's net capital contribution.
- **Formula**: `Total Portfolio Value - Net Deposits`

---

## Success Criteria

### Critical Tests (Must Pass)
- Account creation with valid data
- Buy shares with sufficient funds
- Sell shares that are owned
- Attempt to buy with insufficient funds (rejection)
- Attempt to sell more shares than owned (rejection)
- Portfolio value calculations
- Transaction history accuracy

### High Priority Tests (Should Pass)
- All cash management operations
- Invalid input handling (negative amounts, zero, non-numeric)
- Invalid stock symbols
- Multiple sequential operations
- Data consistency across tabs

### Medium Priority Tests (Nice to Have)
- Keyboard accessibility
- Performance benchmarks
- Large dataset handling
- Edge case values

---

## Known Limitations and Out of Scope

### Out of Scope for Current Testing
- User authentication/login sessions
- Password recovery functionality
- Email verification
- Real-time price streaming
- Market/limit orders
- Stop-loss orders
- Trading fees/commissions
- Real payment gateway integration
- Data export to CSV/PDF
- Graphical charts and visualizations
- Advanced filtering/sorting of history
- Multiple concurrent user sessions

### Platform Limitations
- Limited to supported stock symbols (AAPL, TSLA, GOOGL)
- Simulated pricing via `get_share_price()` API
- No historical price data
- Single-user mode (no concurrent access testing unless specified)

---

## Test Environment

### Required Setup
- **Application URL**: `http://127.0.0.1:7860`
- **Framework**: Playwright Test
- **Seed File**: `tests/seed.spec.ts`
- **Browser**: Chromium (default)

### Pre-Test Checklist
- [ ] Application server is running
- [ ] Database is in clean state (for fresh tests)
- [ ] Test data is prepared
- [ ] Seed script executes successfully
- [ ] Stock price API is accessible

### Post-Test Actions
- Verify all test data is cleaned up
- Check for console errors
- Review transaction logs
- Document any failures with screenshots
- Reset database to clean state for next run

---

## Bug Reporting Template

When a test fails, document the following:

**Test ID**: [Scenario number]  
**Severity**: [Critical/High/Medium/Low]  
**Summary**: [Brief description]  
**Steps to Reproduce**: [Detailed steps]  
**Expected Result**: [What should happen]  
**Actual Result**: [What actually happened]  
**Screenshots**: [If applicable]  
**Console Errors**: [Any browser console errors]  
**Environment**: [Browser, OS, application version]  
**Reproducibility**: [Always/Sometimes/Once]

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-15 | QA Team | Initial comprehensive test plan created |

---

**End of Test Plan**
