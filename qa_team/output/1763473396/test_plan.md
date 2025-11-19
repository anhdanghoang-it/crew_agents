# Trading Simulation Platform - Comprehensive Test Plan

## Application Overview

The Trading Simulation Platform is a Gradio-based web application designed to offer users a realistic stock trading simulation environment. The platform allows users to create and manage virtual trading accounts, perform cash deposits and withdrawals, execute buy and sell orders for stocks, and monitor their portfolio's performance through detailed summaries and transaction histories.

### Core Features

-   **Account Creation**: Users can create new trading accounts with an initial capital deposit.
-   **Cash Management**: Users can deposit and withdraw virtual funds from their accounts.
-   **Stock Trading**: Users can buy and sell shares of supported stocks (e.g., AAPL, TSLA, GOOGL) based on simulated market prices.
-   **Portfolio Tracking**: Users can view their current stock holdings, total portfolio value, and overall profit/loss calculations.
-   **Transaction History**: The application provides a complete, chronological audit trail of all account activities, including deposits, withdrawals, and trades.

### Technical Stack

-   **Frontend**: Gradio web interface featuring a tabbed layout for seamless navigation between features.
-   **Pricing Data**: Utilizes an external `get_share_price()` function to fetch stock prices for trade execution and portfolio valuation.
-   **Data Persistence**: A backend system manages user accounts, transaction logs, and portfolio holdings.

---

## Test Environment & Data

-   **Application URL**: `http://127.0.0.1:7860`
-   **Initial State**: All test scenarios assume the application is in a fresh, clean state unless a specific seeding step is defined.
-   **Test Data**:
    -   **Usernames**: `traderQA` (primary test user), `existingUser` (for duplicate checks), `newUser123`.
    -   **Passwords**: `password123`
    -   **Supported Stock Symbols**: `AAPL`, `TSLA`, `GOOGL`.
    -   **Invalid Stock Symbols**: `XYZ`, `INVALID`.
-   **Mocked Data Assumptions**: For tests involving trading, it is assumed that the `get_share_price(symbol)` function can be mocked to return deterministic prices for consistent test outcomes.

### Note on Test Automation

The element references (`ref: eXX`) used in this plan are derived from accessibility snapshots and are effective for manual testing. For robust, long-term test automation, it is highly recommended to implement and use stable, developer-defined selectors, such as `data-testid` attributes, on interactive UI elements.

---

## Non-Functional Testing Notes

While this plan focuses on functional scenarios, the user stories specify the following non-functional requirements that should be validated through dedicated performance and security testing:

-   **Performance**:
    -   Account creation: should complete within 500ms (US-001).
    -   Cash transactions: should complete within 300ms (US-002).
    -   Trade execution: should complete within 1 second (US-003).
    -   Portfolio refresh: should complete within 1 second (US-004).
-   **Security**:
    -   Password storage must use strong hashing (e.g., bcrypt).
    -   All user inputs must be sanitized to prevent injection attacks.
-   **Reliability**:
    -   The system must gracefully handle failures from the `get_share_price` function and display a user-friendly error.

---

## Test Scenarios

### Epic 1: User Account Creation (US-001)

#### 1.1 Successful Account Creation (Happy Path)

-   **Priority**: Critical
-   **User Story**: US-001 (AC-1)
-   **Seeding Steps**: N/A (fresh state).

**Steps:**
1.  Navigate to the application URL: `http://127.0.0.1:7860`.
2.  In the `textbox "Username" [ref=e26]`, enter `traderQA`.
3.  In the `textbox "Password" [ref=e31]`, enter `password123`.
4.  In the `spinbutton "Initial Deposit Amount ($)" [ref=e35]`, enter `10000`.
5.  Click the `button "Create Account" [ref=e36]`.

**Expected Results:**
-   The `textbox "Status" [disabled] [ref=e42]` displays the message: "Success: Account 'traderQA' created with an initial deposit of $10,000.00."
-   The UI transitions to the main tabbed interface, with the "Portfolio" tab active.
-   On the "Portfolio" tab, the `textbox "Cash Balance ($)" [ref=e83]` shows `$10,000.00`.
-   The `textbox "Total Portfolio Value ($)" [ref=e73]` shows `$10,000.00`.
-   The `textbox "Total Profit / Loss ($)" [ref=e78]` shows `$0.00`.

#### 1.2 Attempt to Create Account with a Duplicate Username

-   **Priority**: Critical
-   **User Story**: US-001 (AC-2)
-   **Seeding Steps**: An account with the username `existingUser` must already be present in the system.

**Steps:**
1.  Navigate to the application URL.
2.  In the `textbox "Username" [ref=e26]`, enter `existingUser`.
3.  In the `textbox "Password" [ref=e31]`, enter any valid password.
4.  In the `spinbutton "Initial Deposit Amount ($)" [ref=e35]`, enter any valid amount.
5.  Click the `button "Create Account" [ref=e36]`.

**Expected Results:**
-   The `textbox "Status" [disabled] [ref=e42]` displays the error message: "Error: Username 'existingUser' is already taken. Please choose a different username."
-   The user remains on the account creation screen.

#### 1.3 Attempt to Create Account with Invalid Deposit (Zero, Negative, Non-Numeric)

-   **Priority**: High
-   **User Story**: US-001 (AC-3)
-   **Seeding Steps**: N/A (fresh state).

**Steps (to be repeated for each invalid value):**
1.  Navigate to the application URL.
2.  In the `textbox "Username" [ref=e26]`, enter `newUser123`.
3.  In the `textbox "Password" [ref=e31]`, enter `password123`.
4.  In the `spinbutton "Initial Deposit Amount ($)" [ref=e35]`, enter an invalid value:
    -   Test Case A: `0`
    -   Test Case B: `-100`
    -   Test Case C: `abc` (if the component allows non-numeric input)
5.  Click the `button "Create Account" [ref=e36]`.

**Expected Results:**
-   For all test cases, the `textbox "Status" [disabled] [ref=e42]` displays the error message: "Error: Initial deposit must be a positive number."
-   The account `newUser123` is not created.

---

### Epic 2: User Manages Cash Balance (US-002)

#### 2.1 Successful Deposit

-   **Priority**: High
-   **User Story**: US-002 (AC-1)
-   **Seeding Steps**: Create a user `traderQA` with an initial deposit of $5,000.

**Steps:**
1.  With user `traderQA`'s account loaded, navigate to the `tab "Cash Management" [ref=e62]`.
2.  Verify the `textbox "Current Cash Balance" [disabled] [ref=e151]` displays `$5,000.00`.
3.  In the `spinbutton "Amount ($)" [ref=e158]`, enter `2000`.
4.  Click the `button "Deposit" [ref=e160]`.
5.  Navigate to the `tab "History" [ref=e64]`.

**Expected Results:**
-   After step 4, the `textbox "Status" [disabled] [ref=e167]` displays: "Success: $2,000.00 deposited. Your new cash balance is $7,000.00."
-   The `textbox "Current Cash Balance" [disabled] [ref=e151]` updates to display `$7,000.00`.
-   On the "History" tab, a new `DEPOSIT` transaction for `$2,000.00` is visible at the top of the list.

#### 2.2 Successful Withdrawal

-   **Priority**: High
-   **User Story**: US-002 (AC-2)
-   **Seeding Steps**: Create a user `traderQA` with an initial deposit of $7,000.

**Steps:**
1.  With user `traderQA`'s account loaded, navigate to the `tab "Cash Management" [ref=e62]`.
2.  Verify the `textbox "Current Cash Balance" [disabled] [ref=e151]` displays `$7,000.00`.
3.  In the `spinbutton "Amount ($)" [ref=e158]`, enter `1500`.
4.  Click the `button "Withdraw" [ref=e161]`.
5.  Navigate to the `tab "History" [ref=e64]`.

**Expected Results:**
-   After step 4, the `textbox "Status" [disabled] [ref=e167]` displays: "Success: $1,500.00 withdrawn. Your new cash balance is $5,500.00."
-   The `textbox "Current Cash Balance" [disabled] [ref=e151]` updates to display `$5,500.00`.
-   On the "History" tab, a new `WITHDRAWAL` transaction for `$1,500.00` is visible at the top of the list.

#### 2.3 Attempt to Withdraw More Than Available Balance

-   **Priority**: High
-   **User Story**: US-002 (AC-3)
-   **Seeding Steps**: Create a user `traderQA` with an initial deposit of $1,000.

**Steps:**
1.  With user `traderQA`'s account loaded, navigate to the `tab "Cash Management" [ref=e62]`.
2.  Verify the `textbox "Current Cash Balance" [disabled] [ref=e151]` displays `$1,000.00`.
3.  In the `spinbutton "Amount ($)" [ref=e158]`, enter `1500`.
4.  Click the `button "Withdraw" [ref=e161]`.

**Expected Results:**
-   The `textbox "Status" [disabled] [ref=e167]` displays the error message: "Error: Insufficient funds. You cannot withdraw more than your available cash balance of $1,000.00."
-   The `textbox "Current Cash Balance" [disabled] [ref=e151]` remains `$1,000.00`.
-   No new transaction is recorded in the history.

#### 2.4 Attempt to Deposit/Withdraw an Invalid Amount

-   **Priority**: Medium
-   **User Story**: US-002 (AC-4)
-   **Seeding Steps**: Create a user `traderQA` with any positive cash balance.

**Steps:**
1.  With user `traderQA`'s account loaded, navigate to the `tab "Cash Management" [ref=e62]`.
2.  In the `spinbutton "Amount ($)" [ref=e158]`, enter `-50`.
3.  Click the `button "Deposit" [ref=e160]`. Verify the expected error.
4.  Click the `button "Withdraw" [ref=e161]`. Verify the expected error.
5.  In the `spinbutton "Amount ($)" [ref=e158]`, enter `0`.
6.  Click the `button "Deposit" [ref=e160]`. Verify the expected error.
7.  Click the `button "Withdraw" [ref=e161]`. Verify the expected error.

**Expected Results:**
-   For all attempts (steps 3, 4, 6, 7), the `textbox "Status" [disabled] [ref=e167]` displays the error message: "Error: Amount must be a positive number."
-   The cash balance remains unchanged.

---

### Epic 3: User Executes Trades (US-003)

#### 3.1 Successful Share Purchase

-   **Priority**: Critical
-   **User Story**: US-003 (AC-1)
-   **Seeding Steps**: Create user `traderQA` with a $10,000 deposit. Mock `get_share_price('AAPL')` to return `$150.00`.

**Steps:**
1.  With user `traderQA` loaded, navigate to the `tab "Trade" [ref=e63]`.
2.  From the `listbox "Action" [ref=e178]`, select "BUY".
3.  In the `textbox "Stock Symbol" [ref=e183]`, enter `AAPL`.
4.  In the `spinbutton "Quantity" [ref=e190]`, enter `10`.
5.  Click the `button "Execute Trade" [ref=e191]`.
6.  Navigate to the `tab "Portfolio" [ref=e61]`.

**Expected Results:**
-   After step 5, the `textbox "Status" [disabled] [ref=e197]` displays: "Success: Bought 10 shares of AAPL at $150.00 each for a total of $1,500.00."
-   On the "Portfolio" tab, the `textbox "Cash Balance ($)" [ref=e83]` shows `$8,500.00`.
-   The "Current Holdings" table (`grid [ref=e92]`) contains a row for `AAPL` with a quantity of `10`.

#### 3.2 Successful Share Sale

-   **Priority**: Critical
-   **User Story**: US-003 (AC-2)
-   **Seeding Steps**: User `traderQA` exists with $8,500 cash and 10 shares of `AAPL`. Mock `get_share_price('AAPL')` to return `$160.00`. (This can follow scenario 3.1).

**Steps:**
1.  With user `traderQA` loaded, navigate to the `tab "Trade" [ref=e63]`.
2.  From the `listbox "Action" [ref=e178]`, select "SELL".
3.  In the `textbox "Stock Symbol" [ref=e183]`, enter `AAPL`.
4.  In the `spinbutton "Quantity" [ref=e190]`, enter `5`.
5.  Click the `button "Execute Trade" [ref=e191]`.
6.  Navigate to the `tab "Portfolio" [ref=e61]`.

**Expected Results:**
-   After step 5, the `textbox "Status" [disabled] [ref=e197]` displays: "Success: Sold 5 shares of AAPL at $160.00 each for a total of $800.00."
-   On the "Portfolio" tab, the `textbox "Cash Balance ($)" [ref=e83]` shows `$9,300.00`.
-   The "Current Holdings" table (`grid [ref=e92]`) updates the `AAPL` row to show a quantity of `5`.

#### 3.3 Attempt to Buy with Insufficient Funds

-   **Priority**: High
-   **User Story**: US-003 (AC-3)
-   **Seeding Steps**: User `traderQA` exists with $1,000 cash. Mock `get_share_price('TSLA')` to return `$300.00`.

**Steps:**
1.  With user `traderQA` loaded, navigate to the `tab "Trade" [ref=e63]`.
2.  Action: "BUY", Symbol: `TSLA`, Quantity: `4`.
3.  Click the `button "Execute Trade" [ref=e191]`.

**Expected Results:**
-   The `textbox "Status" [disabled] [ref=e197]` displays: "Error: Insufficient funds. You need $1,200.00 to buy 4 shares of TSLA, but you only have $1,000.00."
-   Cash balance and portfolio holdings remain unchanged.

#### 3.4 Attempt to Sell More Shares Than Owned

-   **Priority**: High
-   **User Story**: US-003 (AC-4)
-   **Seeding Steps**: User `traderQA` exists and owns 5 shares of `GOOGL`.

**Steps:**
1.  With user `traderQA` loaded, navigate to the `tab "Trade" [ref=e63]`.
2.  Action: "SELL", Symbol: `GOOGL`, Quantity: `10`.
3.  Click the `button "Execute Trade" [ref=e191]`.

**Expected Results:**
-   The `textbox "Status" [disabled] [ref=e197]` displays: "Error: Insufficient shares. You cannot sell 10 shares of GOOGL as you only own 5."
-   Holdings of `GOOGL` remain at 5 shares.

#### 3.5 Attempt to Trade an Invalid Symbol

-   **Priority**: Medium
-   **User Story**: US-003 (AC-5)
-   **Seeding Steps**: Any user account exists. Mock `get_share_price('XYZ')` to return failure/null.

**Steps:**
1.  With any user loaded, navigate to the `tab "Trade" [ref=e63]`.
2.  Action: "BUY", Symbol: `XYZ`, Quantity: `1`.
3.  Click the `button "Execute Trade" [ref=e191]`.

**Expected Results:**
-   The `textbox "Status" [disabled] [ref=e197]` displays: "Error: Invalid stock symbol 'XYZ'. Please use a valid symbol (e.g., AAPL, TSLA, GOOGL)."

#### 3.6 Attempt to Trade an Invalid Quantity

-   **Priority**: Medium
-   **User Story**: US-003 (AC-6)
-   **Seeding Steps**: Any user account exists.

**Steps:**
1.  With any user loaded, navigate to the `tab "Trade" [ref=e63]`.
2.  Action: "BUY", Symbol: `AAPL`.
3.  Attempt to trade with the following quantities, clicking "Execute Trade" each time:
    -   Test Case A: `0`
    -   Test Case B: `-5`
    -   Test Case C: `2.5` (if component allows)

**Expected Results:**
-   For all test cases, the `textbox "Status" [disabled] [ref=e197]` displays the error: "Error: Quantity must be a positive whole number."

---

### Epic 4: User Views Portfolio and Transaction History (US-004)

#### 4.1 View Portfolio Summary with Correct Calculations

-   **Priority**: High
-   **User Story**: US-004 (AC-1)
-   **Seeding Steps**: A user account exists in the following state:
    -   Cash Balance: `$5,000`.
    -   Holdings: 10 shares of `AAPL`, 5 shares of `TSLA`.
    -   Transaction History resulting in a Net Deposit of `$10,000`.
    -   Mock `get_share_price('AAPL')` to return `$150.00`.
    -   Mock `get_share_price('TSLA')` to return `$300.00`.

**Steps:**
1.  Load the seeded user's account.
2.  Navigate to the `tab "Portfolio" [ref=e61]`.
3.  Click the `button "Refresh" [ref=e84]` to ensure latest prices are used.

**Expected Results:**
-   The `textbox "Total Portfolio Value ($)" [ref=e73]` displays `$8,000.00`.
-   The `textbox "Total Profit / Loss ($)" [ref=e78]` displays `-$2,000.00`.
-   The `textbox "Cash Balance ($)" [ref=e83]` displays `$5,000.00`.
-   The "Current Holdings" table (`grid [ref=e92]`) shows two rows:
    -   `AAPL | 10 | $150.00 | $1500.00`
    -   `TSLA | 5 | $300.00 | $1500.00`

#### 4.2 View Populated Transaction History

-   **Priority**: High
-   **User Story**: US-004 (AC-2)
-   **Seeding Steps**: Create a user and perform the following actions in order:
    1.  Initial Deposit: `$20,000`.
    2.  Buy 10 `AAPL` at `$150`.
    3.  Withdraw `$1,000`.
    4.  Sell 5 `GOOGL` at `$100` (assuming user somehow had GOOGL shares).

**Steps:**
1.  Load the seeded user's account.
2.  Navigate to the `tab "History" [ref=e64]`.

**Expected Results:**
-   The transaction history table (`grid [ref=e233]`) displays 4 rows.
-   The rows are in reverse chronological order (SELL, WITHDRAW, BUY, DEPOSIT).
-   Each row contains the correct data (Timestamp, Type, Symbol, Quantity, Price, Total).
-   The `DEPOSIT` and `WITHDRAWAL` rows show `null` or `N/A` for Symbol, Quantity, and Price columns, as per the snapshot (`ref=e278`, `ref=e279`, `ref=e282`).

#### 4.3 View Empty Portfolio for a New User

-   **Priority**: Medium
-   **User Story**: US-004 (AC-3)
-   **Seeding Steps**: Create a new user `traderQA` with an initial deposit of `$10,000` and perform no other actions.

**Steps:**
1.  Load the new user's account.
2.  Navigate to the `tab "Portfolio" [ref=e61]`.
3.  Navigate to the `tab "History" [ref=e64]`.

**Expected Results:**
-   **On the Portfolio tab:**
    -   The "Current Holdings" table (`grid [ref=e92]`) is empty or displays a message like "You do not own any shares."
    -   `textbox "Total Portfolio Value ($)" [ref=e73]` displays `$10,000.00`.
    -   `textbox "Total Profit / Loss ($)" [ref=e78]` displays `$0.00`.
    -   `textbox "Cash Balance ($)" [ref=e83]` displays `$10,000.00`.
-   **On the History tab:**
    -   The transaction table (`grid [ref=e233]`) contains only one entry: the initial `DEPOSIT` of `$10,000.00`.