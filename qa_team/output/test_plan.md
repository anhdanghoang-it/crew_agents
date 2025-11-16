# Trading Simulation Platform - Comprehensive Test Plan

## Application Overview
The Trading Simulation Platform is a Gradio-based web application designed to offer users a virtual environment for stock trading. The platform allows users to create and manage a simulated trading account, perform cash deposits and withdrawals, execute buy and sell orders for stocks, and monitor their portfolio's performance through detailed summaries and transaction histories.

### Core Features
- **Account Creation**: New users can register an account with an initial virtual cash deposit.
- **Cash Management**: Users can deposit and withdraw virtual funds to manage their trading capital.
- **Stock Trading**: Users can buy and sell shares of specific stocks (e.g., AAPL, TSLA, GOOGL).
- **Portfolio Tracking**: The application provides a real-time view of current holdings, total portfolio value, and profit/loss calculations.
- **Transaction History**: A comprehensive log of all user activities, including deposits, withdrawals, buys, and sells, is maintained.

### Technical Stack
- **Frontend**: Gradio web interface featuring a tabbed layout for seamless navigation.
- **Data Backend**: Assumed persistence layer for user accounts, transactions, and holdings.
- **Pricing Service**: Relies on an external `get_share_price()` function to fetch stock prices.

---
## Test Environment Setup
- **Application URL**: `http://127.0.0.1:7860/`
- **Assumptions**: The application is in a fresh, clean state before each test epic begins, unless seeding steps are specified.
- **Supported Stock Symbols**: AAPL, TSLA, GOOGL (as per user stories).

---
## Test Scenarios

### Epic 1: Account Management & Creation (US-001)

#### 1.1 Create New Account Successfully (Happy Path)
**Priority**: Critical   **User Story**: US-001 (AC-1)   **Seeding steps:** N/A (fresh state)
**Steps:**
1.  Navigate to the application URL: `http://127.0.0.1:7860`.
2.  In the "Username" textbox (ref: e26), enter a unique username: `traderQA`.
3.  In the "Password" textbox (ref: e31), enter a secure password: `password123`.
4.  In the "Initial Deposit Amount ($)" spinbutton (ref: e35), enter the amount: `10000`.
5.  Click the "Create Account" button (ref: e36).

**Expected Results:**
- The "Status" textbox (ref: e42) displays the success message: "Success: Account 'traderQA' created with an initial deposit of $10,000.00."
- The UI transitions to the main application view with tabs.
- Navigating to the "Portfolio" tab (ref: e61) shows:
    - "Cash Balance ($)" (ref: e83) is `$10,000.00`.
    - "Total Portfolio Value ($)" (ref: e73) is `$10,000.00`.
    - "Total Profit / Loss ($)" (ref: e78) is `$0.00`.
- Navigating to the "History" tab (ref: e64) shows one transaction: a 'DEPOSIT' of $10,000.00.

#### 1.2 Attempt to Create Account with a Non-Unique Username
**Priority**: Critical   **User Story**: US-001 (AC-2)   **Seeding steps:** An account with username `traderQA` must already exist. This test should run after 1.1.
**Steps:**
1.  Navigate to the application URL: `http://127.0.0.1:7860`.
2.  In the "Username" textbox (ref: e26), enter the existing username: `traderQA`.
3.  Enter any values for password and initial deposit.
4.  Click the "Create Account" button (ref: e36).

**Expected Results:**
- The account creation is rejected.
- The "Status" textbox (ref: e42) displays the error message: "Error: Username 'traderQA' is already taken. Please choose a different username."

#### 1.3 Attempt to Create Account with Invalid Initial Deposit
**Priority**: High   **User Story**: US-001 (AC-3)   **Seeding steps:** N/A (fresh state)
**Steps:**
1.  Navigate to the application URL: `http://127.0.0.1:7860`.
2.  Enter a unique username and password.
3.  In the "Initial Deposit Amount ($)" spinbutton (ref: e35), enter a negative value: `-100`.
4.  Click the "Create Account" button (ref: e36).
5.  Change the deposit amount to zero: `0`.
6.  Click the "Create Account" button (ref: e36).
7.  (If possible) attempt to enter a non-numeric value like `abc`.

**Expected Results:**
- For steps 4 and 6, the account creation is rejected.
- The "Status" textbox (ref: e42) displays the error message: "Error: Initial deposit must be a positive number." for both attempts.
- The `gr.Number` component should inherently prevent non-numeric input, but if it allows it, the backend validation should trigger the same error.

---
### Epic 2: Cash Management (US-002)

#### 2.1 Successful Deposit and Balance Update
**Priority**: High   **User Story**: US-002 (AC-1)   **Seeding steps:** Create an account `traderQA` with an initial deposit of $10,000.
**Steps:**
1.  Complete the account creation for `traderQA` with an initial deposit of $10,000.
2.  Navigate to the "Cash Management" tab (ref: e62).
3.  Verify the "Current Cash Balance" (ref: e151) is `$10,000.00`.
4.  In the "Amount ($)" spinbutton (ref: e158), enter `2000`.
5.  Click the "Deposit" button (ref: e160).

**Expected Results:**
- The "Status" textbox (ref: e167) displays: "Success: $2,000.00 deposited. Your new cash balance is $12,000.00."
- The "Current Cash Balance" (ref: e151) updates to display `$12,000.00`.
- Navigating to the "History" tab (ref: e64) shows a new 'DEPOSIT' transaction for $2,000.00, listed above the initial deposit.

#### 2.2 Successful Withdrawal and Balance Update
**Priority**: High   **User Story**: US-002 (AC-2)   **Seeding steps:** Create an account `traderQA` with a cash balance of $7,000.
**Steps:**
1.  Create an account for `traderQA` with an initial deposit of $7,000.
2.  Navigate to the "Cash Management" tab (ref: e62).
3.  Verify the "Current Cash Balance" (ref: e151) is `$7,000.00`.
4.  In the "Amount ($)" spinbutton (ref: e158), enter `1500`.
5.  Click the "Withdraw" button (ref: e161).

**Expected Results:**
- The "Status" textbox (ref: e167) displays: "Success: $1,500.00 withdrawn. Your new cash balance is $5,500.00."
- The "Current Cash Balance" (ref: e151) updates to display `$5,500.00`.
- Navigating to the "History" tab (ref: e64) shows a new 'WITHDRAWAL' transaction for $1,500.00.

#### 2.3 Attempt to Withdraw More Than Available Balance
**Priority**: High   **User Story**: US-002 (AC-3)   **Seeding steps:** Create an account `traderQA` with a cash balance of $1,000.
**Steps:**
1.  Create an account `traderQA` with an initial deposit of $1,000.
2.  Navigate to the "Cash Management" tab (ref: e62).
3.  Verify the "Current Cash Balance" (ref: e151) is `$1,000.00`.
4.  In the "Amount ($)" spinbutton (ref: e158), enter `1500`.
5.  Click the "Withdraw" button (ref: e161).

**Expected Results:**
- The transaction is rejected.
- The "Status" textbox (ref: e167) displays the error message: "Error: Insufficient funds. You cannot withdraw more than your available cash balance of $1,000.00."
- The "Current Cash Balance" (ref: e151) remains unchanged at `$1,000.00`.

#### 2.4 Attempt to Deposit/Withdraw an Invalid Amount
**Priority**: Medium   **User Story**: US-002 (AC-4)   **Seeding steps:** Create an account `traderQA` with any positive balance.
**Steps:**
1.  Create an account `traderQA` with an initial deposit of $5,000.
2.  Navigate to the "Cash Management" tab (ref: e62).
3.  In the "Amount ($)" spinbutton (ref: e158), enter `-50`.
4.  Click the "Deposit" button (ref: e160).
5.  Verify the error message appears.
6.  Click the "Withdraw" button (ref: e161).
7.  Verify the error message appears.

**Expected Results:**
- For both steps 4 and 6, the transaction is rejected.
- The "Status" textbox (ref: e167) displays the error message: "Error: Amount must be a positive number."
- The cash balance remains unchanged.

---
### Epic 3: Trading and Execution (US-003)

#### 3.1 Successful Share Purchase
**Priority**: Critical   **User Story**: US-003 (AC-1)   **Seeding steps:** Create an account `traderQA` with a cash balance of $10,000.
**Steps:**
1.  Create an account `traderQA` with an initial deposit of $10,000.
2.  Navigate to the "Trade" tab (ref: e63).
3.  Select "BUY" in the "Action" listbox (ref: e178).
4.  In the "Stock Symbol" textbox (ref: e183), enter `AAPL`.
5.  In the "Quantity" spinbutton (ref: e190), enter `10`.
6.  Click the "Execute Trade" button (ref: e191). (Assume `get_share_price('AAPL')` returns $150).

**Expected Results:**
- The "Status" textbox (ref: e197) displays: "Success: Bought 10 shares of AAPL at $150.00 each for a total of $1,500.00."
- Navigate to the "Portfolio" tab (ref: e61):
    - "Cash Balance ($)" (ref: e83) is now `$8,500.00`.
    - The "Current Holdings" table (ref: e92) shows a new row for "AAPL" with quantity "10".
- Navigate to the "History" tab (ref: e64) and verify a new 'BUY' transaction for 10 shares of AAPL is recorded.

#### 3.2 Successful Share Sale
**Priority**: Critical   **User Story**: US-003 (AC-2)   **Seeding steps:** Requires a user to own shares. This test depends on the successful completion of 3.1.
**Steps:**
1.  Perform all steps from test case 3.1.
2.  Navigate to the "Trade" tab (ref: e63).
3.  Select "SELL" in the "Action" listbox (ref: e178).
4.  In the "Stock Symbol" textbox (ref: e183), enter `AAPL`.
5.  In the "Quantity" spinbutton (ref: e190), enter `5`.
6.  Click the "Execute Trade" button (ref: e191). (Assume `get_share_price('AAPL')` now returns $160).

**Expected Results:**
- The "Status" textbox (ref: e197) displays: "Success: Sold 5 shares of AAPL at $160.00 each for a total of $800.00."
- Navigate to the "Portfolio" tab (ref: e61):
    - "Cash Balance ($)" (ref: e83) is now `$9,300.00` ($8,500 + $800).
    - The "Current Holdings" table (ref: e92) shows the quantity for "AAPL" is now "5".
- Navigate to the "History" tab (ref: e64) and verify a new 'SELL' transaction for 5 shares of AAPL is recorded.

#### 3.3 Attempt to Buy with Insufficient Funds
**Priority**: High   **User Story**: US-003 (AC-3)   **Seeding steps:** Create an account `traderQA` with a cash balance of $1,000.
**Steps:**
1.  Create an account `traderQA` with an initial deposit of $1,000.
2.  Navigate to the "Trade" tab (ref: e63).
3.  Select "BUY", enter `TSLA` as the symbol, and `4` as the quantity.
4.  Click the "Execute Trade" button (ref: e191). (Assume `get_share_price('TSLA')` returns $300, for a total cost of $1,200).

**Expected Results:**
- The transaction is rejected.
- The "Status" textbox (ref: e197) displays: "Error: Insufficient funds. You need $1,200.00 to buy 4 shares of TSLA, but you only have $1,000.00."
- Cash balance and holdings remain unchanged.

#### 3.4 Attempt to Sell More Shares Than Owned
**Priority**: High   **User Story**: US-003 (AC-4)   **Seeding steps:** Create an account, buy 5 shares of 'GOOGL'.
**Steps:**
1.  Create an account `traderQA` with a sufficient deposit (e.g., $10,000).
2.  Buy 5 shares of `GOOGL`.
3.  Navigate to the "Trade" tab (ref: e63).
4.  Select "SELL", enter `GOOGL` as the symbol, and `10` as the quantity.
5.  Click the "Execute Trade" button (ref: e191).

**Expected Results:**
- The transaction is rejected.
- The "Status" textbox (ref: e197) displays: "Error: Insufficient shares. You cannot sell 10 shares of GOOGL as you only own 5."
- Holdings remain unchanged.

#### 3.5 Attempt to Trade an Invalid Symbol or Invalid Quantity
**Priority**: Medium   **User Story**: US-003 (AC-5, AC-6)   **Seeding steps:** Create an account `traderQA`.
**Steps:**
1.  Create an account `traderQA` with a deposit of $10,000.
2.  Navigate to the "Trade" tab (ref: e63).
3.  Attempt to trade with an invalid symbol: Enter `XYZ` in the "Stock Symbol" textbox (ref: e183) and click "Execute Trade".
4.  Attempt to trade with an invalid quantity: Enter a valid symbol (`AAPL`) and enter `0` in the "Quantity" spinbutton (ref: e190), then click "Execute Trade".
5.  Repeat step 4 with a negative quantity `-5`.

**Expected Results:**
- For step 3, the "Status" textbox (ref: e197) displays: "Error: Invalid stock symbol 'XYZ'. Please use a valid symbol (e.g., AAPL, TSLA, GOOGL)."
- For steps 4 and 5, the "Status" textbox (ref: e197) displays: "Error: Quantity must be a positive whole number."

---
### Epic 4: Portfolio and History Reporting (US-004)

#### 4.1 Comprehensive End-to-End User Journey and Final Portfolio Verification
**Priority**: Critical   **User Story**: US-004 (AC-1, AC-2) and others.   **Seeding steps:** N/A (fresh state)
**Steps:**
1.  **Account Creation (US-001):** Create account `traderE2E` with an initial deposit of $12,000.
2.  **Cash Management (US-002):** Navigate to the "Cash Management" tab. Withdraw $2,000. *Net Deposit is now $10,000.*
3.  **First Purchase (US-003):** Navigate to the "Trade" tab. Buy 10 shares of `AAPL`. (Assume price is $150, cost $1,500). *Cash is now $8,500.*
4.  **Second Purchase (US-003):** On the "Trade" tab, buy 5 shares of `TSLA`. (Assume price is $300, cost $1,500). *Cash is now $7,000.*
5.  **Portfolio Check:** Navigate to the "Portfolio" tab (ref: e61). (Assume current prices are still AAPL=$150, TSLA=$300).
6.  **History Check:** Navigate to the "History" tab (ref: e64).

**Expected Results:**
- **Step 5 (Portfolio View):**
    - "Cash Balance ($)" (ref: e83) is `$7,000.00`.
    - "Current Holdings" (ref: e92) displays two rows: {Symbol: AAPL, Quantity: 10} and {Symbol: TSLA, Quantity: 5}.
    - The calculated "Total Value of Shares" is `(10 * $150) + (5 * $300) = $3,000`.
    - "Total Portfolio Value ($)" (ref: e73) is `$7,000 (cash) + $3,000 (shares) = $10,000.00`.
    - "Total Profit / Loss ($)" (ref: e78) is `$10,000 (Portfolio Value) - $10,000 (Net Deposits) = $0.00`.
- **Step 6 (History View):**
    - The transaction history table (ref: e233) shows 4 transactions in reverse chronological order (most recent first):
        1.  BUY, TSLA, 5, $300.00, $1,500.00
        2.  BUY, AAPL, 10, $150.00, $1,500.00
        3.  WITHDRAWAL, N/A, N/A, N/A, $2,000.00
        4.  DEPOSIT, N/A, N/A, N/A, $12,000.00

#### 4.2 Verify Portfolio After Price Change and Refresh
**Priority**: High   **User Story**: US-004 (AC-1)   **Seeding steps:** Follows directly from test case 4.1.
**Steps:**
1.  Ensure the application is in the final state of test case 4.1.
2.  (Simulate price change) Assume the backend `get_share_price()` function now returns `AAPL`=$160 and `TSLA`=$280.
3.  On the "Portfolio" tab (ref: e61), click the "Refresh" button (ref: e84).

**Expected Results:**
- The portfolio values update correctly:
    - "Cash Balance ($)" (ref: e83) remains `$7,000.00`.
    - The "Total Value of Shares" is recalculated to `(10 * $160) + (5 * $280) = $1,600 + $1,400 = $3,000`.
    - "Total Portfolio Value ($)" (ref: e73) remains `$7,000 + $3,000 = $10,000.00`.
    - "Total Profit / Loss ($)" (ref: e78) remains `$10,000 - $10,000 = $0.00`.
    - The "Current Holdings" table (ref: e92) updates to show the new prices and total values for each holding.