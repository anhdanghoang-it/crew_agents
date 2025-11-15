# Trading Simulation Platform - Comprehensive Test Plan

## Executive Summary

This test plan covers the Trading Simulation Platform available at http://127.0.0.1:7860/. The application enables users to create accounts, manage cash balances, execute trades, and view portfolio and transaction history. The backend is implemented in Python, and the frontend uses Gradio. All user-facing success and error messages, UI/UX flows, and business logic are derived from the provided user stories and technical design documents.

---

## Test Scenarios

### 1. Account Creation

#### 1.1 Successful Account Creation (Happy Path)
**Assumptions:** No existing user with username 'trader123'.
**Steps:**
1. Navigate to the account creation screen.
2. Enter username: `trader123`.
3. Enter password: `password123`.
4. Enter initial deposit: `10000`.
5. Click `Create Account`.
**Expected Results:**
- Account is created.
- Initial cash balance is $10,000.
- Status box displays: `Success: Account 'trader123' created with an initial deposit of $10,000.00.`
- A 'DEPOSIT' transaction for $10,000 is recorded in history.

#### 1.2 Attempt to Create Account with Non-Unique Username
**Assumptions:** User 'trader123' already exists.
**Steps:**
1. Enter username: `trader123`.
2. Enter password and deposit.
3. Click `Create Account`.
**Expected Results:**
- Account creation is rejected.
- Status box displays: `Error: Username 'trader123' is already taken. Please choose a different username.`

#### 1.3 Attempt to Create Account with Invalid Initial Deposit
**Steps:**
1. Enter valid username and password.
2. Enter deposit: `abc`, `0`, or `-100`.
3. Click `Create Account`.
**Expected Results:**
- Account creation is rejected.
- Status box displays: `Error: Initial deposit must be a positive number.`

---

### 2. Cash Management (Deposit/Withdraw)

#### 2.1 Successful Deposit
**Assumptions:** User is logged in with $5,000 balance.
**Steps:**
1. Go to `Cash Management` tab.
2. Enter amount: `2000`.
3. Click `Deposit`.
**Expected Results:**
- Cash balance updates to $7,000.
- Status box displays: `Success: $2,000.00 deposited. Your new cash balance is $7,000.00.`
- 'DEPOSIT' transaction recorded.

#### 2.2 Successful Withdrawal
**Assumptions:** User has $7,000 balance.
**Steps:**
1. Enter amount: `1500`.
2. Click `Withdraw`.
**Expected Results:**
- Cash balance updates to $5,500.
- Status box displays: `Success: $1,500.00 withdrawn. Your new cash balance is $5,500.00.`
- 'WITHDRAWAL' transaction recorded.

#### 2.3 Attempt to Withdraw More Than Available Balance
**Assumptions:** User has $1,000 balance.
**Steps:**
1. Enter amount: `1500`.
2. Click `Withdraw`.
**Expected Results:**
- Transaction is rejected.
- Status box displays: `Error: Insufficient funds. You cannot withdraw more than your available cash balance of $1,000.00.`

#### 2.4 Attempt to Deposit/Withdraw Invalid Amount
**Steps:**
1. Enter amount: `-50` or `0`.
2. Click `Deposit` or `Withdraw`.
**Expected Results:**
- Transaction is rejected.
- Status box displays: `Error: Amount must be a positive number.`

---

### 3. Trade Execution (Buy/Sell Shares)

#### 3.1 Successful Share Purchase
**Assumptions:** User has $10,000 cash, 0 AAPL shares, AAPL price is $150.
**Steps:**
1. Go to `Trade` tab.
2. Select `BUY`.
3. Enter symbol: `AAPL`.
4. Enter quantity: `10`.
5. Click `Execute Trade`.
**Expected Results:**
- Cash balance reduces to $8,500.
- Holdings show 10 AAPL shares.
- Status box displays: `Success: Bought 10 shares of AAPL at $150.00 each for a total of $1,500.00.`
- 'BUY' transaction recorded.

#### 3.2 Successful Share Sale
**Assumptions:** User has $8,500 cash, 10 AAPL shares, AAPL price is $160.
**Steps:**
1. Select `SELL`.
2. Enter symbol: `AAPL`.
3. Enter quantity: `5`.
4. Click `Execute Trade`.
**Expected Results:**
- Cash balance increases to $9,300.
- Holdings show 5 AAPL shares.
- Status box displays: `Success: Sold 5 shares of AAPL at $160.00 each for a total of $800.00.`
- 'SELL' transaction recorded.

#### 3.3 Attempt to Buy with Insufficient Funds
**Assumptions:** User has $1,000 cash, TSLA price is $300.
**Steps:**
1. Select `BUY`.
2. Enter symbol: `TSLA`.
3. Enter quantity: `4`.
4. Click `Execute Trade`.
**Expected Results:**
- Transaction is rejected.
- Status box displays: `Error: Insufficient funds. You need $1,200.00 to buy 4 shares of TSLA, but you only have $1,000.00.`

#### 3.4 Attempt to Sell More Shares Than Owned
**Assumptions:** User owns 5 GOOGL shares.
**Steps:**
1. Select `SELL`.
2. Enter symbol: `GOOGL`.
3. Enter quantity: `10`.
4. Click `Execute Trade`.
**Expected Results:**
- Transaction is rejected.
- Status box displays: `Error: Insufficient shares. You cannot sell 10 shares of GOOGL as you only own 5.`

#### 3.5 Attempt to Trade an Invalid Symbol
**Steps:**
1. Enter symbol: `XYZ`.
2. Enter valid quantity.
3. Click `Execute Trade`.
**Expected Results:**
- Transaction is rejected.
- Status box displays: `Error: Invalid stock symbol 'XYZ'. Please use a valid symbol (e.g., AAPL, TSLA, GOOGL).`

#### 3.6 Attempt to Trade an Invalid Quantity
**Steps:**
1. Enter quantity: `0`, `-5`, or `2.5`.
2. Click `Execute Trade`.
**Expected Results:**
- Transaction is rejected.
- Status box displays: `Error: Quantity must be a positive whole number.`

---

### 4. Portfolio & Transaction History

#### 4.1 View Portfolio Summary with Correct Calculations
**Assumptions:** User has $5,000 cash, 10 AAPL shares, 5 TSLA shares, total deposits $12,000, withdrawals $2,000, AAPL price $150, TSLA price $300.
**Steps:**
1. Go to `Portfolio` tab.
2. Click `Refresh`.
**Expected Results:**
- Holdings: "AAPL: 10 shares", "TSLA: 5 shares".
- Total Value of Shares: $3,000.
- Total Portfolio Value: $8,000.
- Profit/Loss: -$2,000.
- All values displayed in respective fields.

#### 4.2 View Transaction History
**Assumptions:** User has made several transactions.
**Steps:**
1. Go to `History` tab.
**Expected Results:**
- All transactions listed in reverse chronological order.
- Each entry includes timestamp, type, symbol, quantity, price, total amount.

#### 4.3 View Empty Portfolio and History
**Assumptions:** New user, only initial deposit.
**Steps:**
1. Go to `Portfolio` tab.
**Expected Results:**
- Holdings section is empty or shows "No shares owned".
- Total Portfolio Value equals initial deposit.
- Profit/Loss is $0.
2. Go to `History` tab.
**Expected Results:**
- Only initial 'DEPOSIT' transaction is listed.

---

## Non-Functional & Edge Case Testing

### 5.1 Performance
- Account creation, deposit/withdrawal, and trade execution should complete within specified time (see user stories).
- Portfolio and history views should update within 1 second of user action.

### 5.2 Security & Data Integrity
- Passwords are not visible in UI after entry.
- All user inputs are sanitized; invalid or malicious input is rejected with appropriate error messages.
- Transactions are atomic; no partial updates.

### 5.3 Scalability
- History view should handle 1,000+ transactions without UI lag.

### 5.4 UI/UX Validation
- All status messages match those defined in user stories.
- Gradio components are present and correctly labeled.
- Tab navigation works as described.

---

## Success Criteria
- All scenarios above pass as described.
- All error messages match exactly.
- UI/UX matches wireframes and component mapping.
- No unhandled exceptions or crashes during normal or edge case usage.

## Failure Conditions
- Any scenario produces incorrect results, missing or incorrect messages, or UI does not update as expected.
- Any operation results in a crash, unhandled exception, or security/data integrity issue.

---

## Documentation
- This test plan is suitable for manual QA, automated E2E, and developer validation. Each scenario is independent and can be run in any order.
