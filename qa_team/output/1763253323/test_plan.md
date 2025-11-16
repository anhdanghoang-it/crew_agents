Thought: The user wants me to act as an Expert Web Test Planner and create a comprehensive test plan for the provided set of user stories concerning a Trading Simulation Platform built with Gradio.

I need to analyze the four user stories (US-001 to US-004), their acceptance criteria, and the provided Gradio UI snapshots to design detailed, actionable, and robust test scenarios.

The test plan must follow the provided structure:
1.  **Application Overview/Executive Summary.**
2.  **Test Environment Setup.**
3.  **Detailed Test Scenarios** categorized by Epic/User Story (US-001, US-002, US-003, US-004).

I must ensure coverage of:
*   Happy paths (AC-1 in most cases).
*   Negative tests/Edge cases (invalid inputs, insufficient funds/shares, unique constraints).
*   Functional requirements (correct calculations, UI updates, transaction recording).
*   Non-functional requirements (performance, security, data integrity, handling external API failures).

**Pre-computation/Assumptions for Scenarios:**
*   A base test user (`traderQA`) will be created in Scenario 1.1 with $10,000.
*   The `get_share_price()` function is simulated for predictable results:
    *   AAPL Price: $150.00
    *   TSLA Price: $300.00
    *   GOOGL Price: $200.00 (Assumed for diversification testing)

---
### **Detailed Plan Outline:**

**US-001: Account Creation**
1.1 Happy Path Account Creation (AC-1).
1.2 Non-Unique Username rejection (AC-2).
1.3 Invalid Deposit Amounts (Zero, Negative, Non-numeric) (AC-3).
1.4 Boundary Condition: Minimum deposit ($0.01).

**US-002: Cash Management**
*Prerequisite: Account `traderQA` with $10,000.*
2.1 Successful Deposit (AC-1).
2.2 Successful Withdrawal (AC-2).
2.3 Insufficient Funds Withdrawal (AC-3).
2.4 Invalid Amount Deposit/Withdrawal (Zero/Negative) (AC-4).
2.5 Boundary Condition: Withdrawing the exact available balance.

**US-003: Trading**
*Prerequisite: Account `traderQA` after 2.1/2.2, e.g., $10,000 cash balance for clean testing.* (Will require setting up the cash balance before this section).
3.1 Successful Buy Order (AAPL, AC-1).
3.2 Successful Sell Order (AAPL, AC-2).
3.3 Insufficient Funds for Buy (AC-3).
3.4 Attempt to Sell More Shares Than Owned (AC-4).
3.5 Invalid Stock Symbol (AC-5).
3.6 Invalid Quantity (Zero, Negative, Non-integer) (AC-6).
3.7 Non-Functional: Handling API Failure for Price Retrieval (Simulated).

**US-004: Portfolio and History**
*Prerequisite: Account `traderQA` after performing 3-5 transactions.* (Will use the results of 1.1, 2.1, 3.1, 3.2, 2.2 to verify this).
4.1 Portfolio View: Correct Calculation Verification (AC-1).
4.2 History View: Transaction Auditing and Order (AC-2).
4.3 Portfolio View: Zero/Empty Holdings State (AC-3 - Initial state verification).
4.4 Non-Functional: Portfolio Refresh Performance.

I will structure the test plan according to the required markdown format. I need to be precise with the Gradio component labels identified in the snapshots (e.g., "spinbutton 'Initial Deposit Amount ($)'", "textbox 'Current Cash Balance'").

Let's start drafting the content.

---
### **Scenario Data Setup (Internal calculation for verification)**

1.  **Initial State (After 1.1):** Cash $10,000. Net Deposits $10,000. P/L $0.
2.  **Scenario 2.1 (Deposit $2,000):** Cash $12,000. Net Deposits $12,000.
3.  **Scenario 3.1 (Buy 10 AAPL @ $150):** Cost $1,500. Cash $10,500. Holdings: 10 AAPL. Net Deposits $12,000.
4.  **Scenario 3.2 (Sell 5 AAPL @ $160):** Revenue $800. Cash $11,300. Holdings: 5 AAPL. Net Deposits $12,000.
5.  **Scenario 2.2 (Withdraw $1,300):** Cash $10,000. Net Deposits $10,700. Holdings: 5 AAPL.

*Final state before 4.1:*
*   Cash: $10,000
*   Holdings: 5 AAPL
*   Net Deposits: $10,700
*   AAPL Price (current, assumed): $170 (Simulated gain for P/L test)
*   Total Share Value: 5 * $170 = $850
*   Total Portfolio Value: $10,000 + $850 = $10,850
*   P/L: $10,850 - $10,700 = $150.00 (Profit)

I will ensure the steps for subsequent scenarios build on successful previous states, clearly defining the starting point. I will use a separate setup step for the complex US-004 verification.

I will use `traderQA` as the standard test user.# Trading Simulation Platform - Comprehensive Test Plan

## Application Overview
The Trading Simulation Platform is a Gradio-based web application designed to allow users to manage a virtual trading account. It supports core financial functionalities, including account management, simulated cash transactions (deposits/withdrawals), stock trading (buy/sell), and performance tracking (portfolio view and transaction history).

### Core Features
*   **Account Creation (US-001):** Primary entry point, handling initial deposits and unique username validation.
*   **Cash Management (US-002):** Deposit and withdrawal functionality, enforcing positive balance constraints.
*   **Stock Trading (US-003):** Execution of buy and sell orders based on current prices from a simulated external API, including validation of funds and holdings.
*   **Reporting (US-004):** Calculation and display of complex metrics like Total Portfolio Value, Net Deposits, and Profit/Loss, alongside a full transaction history audit trail.

### Technical Environment
*   **Frontend:** Gradio web interface.
*   **Pricing Mechanism:** Simulated external function `get_share_price(Symbol)` returning known values for testing.
*   **Dependencies:** US-001 must be completed before accessing other features (US-002, US-003, US-004).

### Test Environment Setup
**Target URL**: `http://127.0.0.1:7860/`
**Test User Identity**: `traderQA`
**Test Data Assumptions (Simulated Prices)**:
| Symbol | Initial Price (Buy Test) | Subsequent Price (Sell/Portfolio Test) |
| :----- | :----------------------- | :------------------------------------- |
| AAPL   | $150.00                  | $160.00                                |
| TSLA   | $300.00                  | $320.00                                |
| GOOGL  | $200.00                  | $200.00                                |

---
## Test Scenarios

### Epic 1: Account Creation (US-001)

#### 1.1 Successful Account Creation and Initial State Verification (AC-1, AC-3)
**Priority**: Critical
**Objective**: Verify the happy path for creating a new account and confirming the initial state of the portfolio and history.
**Starting State**: Application launch screen (Account Creation Form).

| Step | Action | Expected Outcome |
| :--- | :----- | :--------------- |
| 1. | Navigate to the application URL. | Account Creation form is visible (Snapshot US-001). |
| 2. | Enter unique Username: `traderQA` | Input field accepts text. |
| 3. | Enter Password: `password123` | Input field masks text (type="password"). |
| 4. | Enter Initial Deposit Amount: `10000.00` | Input field accepts the positive numeric value. |
| 5. | Click the "Create Account" button. | Status textbox displays: "Success: Account 'traderQA' created with an initial deposit of $10,000.00." |
| 6. | Navigate to the "Portfolio" tab. | The Portfolio tab loads (Snapshot US-004 - Portfolio View). |
| 7. | Verify portfolio metrics. | Total Portfolio Value: `$10,000.00` Cash Balance: `$10,000.00` Total Profit / Loss: `$0.00` |
| 8. | Navigate to the "History" tab. | The History tab loads (Snapshot US-004 - History View). |
| 9. | Verify the transaction history audit. | One transaction exists: Type `DEPOSIT`, Total `$10,000.00`. |

#### 1.2 Attempt to Create Account with Existing Username (AC-2)
**Priority**: High
**Objective**: Verify that the system enforces the unique username constraint.
**Starting State**: `traderQA` account already exists.

| Step | Action | Expected Outcome |
| :--- | :----- | :--------------- |
| 1. | Reload or return to the Account Creation screen. | Form is ready for new input. |
| 2. | Enter Username: `traderQA` (The existing username). | Input accepted. |
| 3. | Enter Password: `diffpassword456` and Deposit: `5000`. | Inputs accepted. |
| 4. | Click the "Create Account" button. | Account creation is rejected. |
| 5. | Verify error message in the Status textbox. | Status displays: "Error: Username 'traderQA' is already taken. Please choose a different username." |

#### 1.3 Boundary Testing: Invalid Initial Deposit (AC-3)
**Priority**: High
**Objective**: Verify input validation for initial deposit amounts (non-numeric, zero, negative).
**Starting State**: Account Creation Form.

| Step | Action | Input | Expected Outcome |
| :--- | :----- | :---- | :--------------- |
| 1. | Attempt creation with non-numeric value. | Deposit: `abc` | Status displays: "Error: Initial deposit must be a positive number." (Or specific UI validation preventing non-numeric input if implemented by Gradio Number component) |
| 2. | Attempt creation with zero. | Deposit: `0` | Status displays: "Error: Initial deposit must be a positive number." |
| 3. | Attempt creation with negative value. | Deposit: `-100` | Status displays: "Error: Initial deposit must be a positive number." |
| 4. | Attempt creation with minimum positive value. | Deposit: `0.01` | Account creation succeeds, cash balance is `$0.01`. |

---
### Epic 2: Cash Management (US-002)

**Prerequisite Setup**: User `traderQA` logged in with a cash balance of **$10,000.00** (from Scenario 1.1).

#### 2.1 Successful Fund Deposit (AC-1)
**Priority**: High
**Objective**: Verify that cash deposits correctly increase the balance and record a transaction.
**Starting State**: Cash Management Tab, Balance: $10,000.00.

| Step | Action | Expected Outcome |
| :--- | :----- | :--------------- |
| 1. | Navigate to the "Cash Management" tab (Snapshot US-002). | Current Cash Balance textbox shows `$10,000.00`. |
| 2. | Enter Amount: `2000.00` into the `Amount ($)` spinbutton. | Input accepted. |
| 3. | Click the "Deposit" button. | Transaction processes successfully. |
| 4. | Verify the Status message. | Status displays: "Success: $2,000.00 deposited. Your new cash balance is $12,000.00." |
| 5. | Verify the updated Cash Balance component. | Current Cash Balance shows `$12,000.00`. |
| 6. | Navigate to the "History" tab. | A new `DEPOSIT` transaction for `$2,000.00` is recorded in reverse chronological order. |
**Post-Condition**: Cash Balance is **$12,000.00**. Net Deposits are **$12,000.00**.

#### 2.2 Successful Fund Withdrawal (AC-2)
**Priority**: High
**Objective**: Verify that cash withdrawals correctly decrease the balance without exceeding it.
**Starting State**: Cash Management Tab, Balance: $12,000.00.

| Step | Action | Expected Outcome |
| :--- | :----- | :--------------- |
| 1. | Navigate to the "Cash Management" tab. | Current Cash Balance textbox shows `$12,000.00`. |
| 2. | Enter Amount: `1500.00` into the `Amount ($)` spinbutton. | Input accepted. |
| 3. | Click the "Withdraw" button. | Transaction processes successfully. |
| 4. | Verify the Status message. | Status displays: "Success: $1,500.00 withdrawn. Your new cash balance is $10,500.00." |
| 5. | Verify the updated Cash Balance component. | Current Cash Balance shows `$10,500.00`. |
| 6. | Navigate to the "History" tab. | A new `WITHDRAWAL` transaction for `$1,500.00` is recorded. |
**Post-Condition**: Cash Balance is **$10,500.00**. Net Deposits are **$10,500.00** (12,000 - 1,500).

#### 2.3 Attempt to Withdraw Insufficient Funds (AC-3)
**Priority**: Critical
**Objective**: Ensure the system prevents over-withdrawal.
**Starting State**: Cash Management Tab, Balance: $10,500.00.

| Step | Action | Expected Outcome |
| :--- | :----- | :--------------- |
| 1. | Enter Amount: `10500.01` (1 penny more than available). | Input accepted. |
| 2. | Click the "Withdraw" button. | Transaction is rejected. |
| 3. | Verify the Status message. | Status displays: "Error: Insufficient funds. You cannot withdraw more than your available cash balance of $10,500.00." (Note: The error message might show the exact current balance based on implementation). |
| 4. | Verify that the Current Cash Balance remains unchanged. | Current Cash Balance shows `$10,500.00`. |
| 5. | Navigate to History. | No new transaction is recorded. |

#### 2.4 Boundary Condition: Withdrawing Exact Available Balance
**Priority**: Medium
**Objective**: Verify that withdrawing the full balance is permitted.
**Starting State**: Cash Management Tab, Balance: $10,500.00.

| Step | Action | Expected Outcome |
| :--- | :----- | :--------------- |
| 1. | Enter Amount: `10500.00` (The exact available balance). | Input accepted. |
| 2. | Click the "Withdraw" button. | Transaction processes successfully. |
| 3. | Verify the Status message. | Status displays successful withdrawal confirmation. |
| 4. | Verify the updated Cash Balance component. | Current Cash Balance shows `$0.00`. |
| 5. | Navigate to History. | A new `WITHDRAWAL` transaction for `$10,500.00` is recorded. |
**Post-Condition**: Cash Balance is **$0.00**. Net Deposits are **$0.00**. (10,500 - 10,500).

---
### Epic 3: Trading Execution (US-003)

**Prerequisite Setup**: Resetting cash for trading test.
1.  Deposit $10,000.00 (New Cash Balance: $10,000.00, Net Deposits: $10,000.00).
2.  Holdings: 0 shares.

#### 3.1 Successful Share Purchase (AC-1)
**Priority**: Critical
**Objective**: Verify that a BUY transaction correctly reduces cash and increases holdings. (AAPL Price: $150.00).
**Starting State**: Trade Tab, Cash Balance: $10,000.00.

| Step | Action | Expected Outcome |
| :--- | :----- | :--------------- |
| 1. | Navigate to the "Trade" tab (Snapshot US-003). | Form is ready for trading input. |
| 2. | Select Action: `BUY` from the dropdown. | Dropdown displays `BUY`. |
| 3. | Enter Stock Symbol: `AAPL`. | Textbox accepts input. |
| 4. | Enter Quantity: `10`. | Input accepted. (Total cost: 10 * $150.00 = $1,500.00). |
| 5. | Click the "Execute Trade" button. | Transaction processes successfully. |
| 6. | Verify the Status message. | Status displays: "Success: Bought 10 shares of AAPL at $150.00 each for a total of $1,500.00." |
| 7. | Navigate to the "Portfolio" tab and refresh. | Cash Balance updates to `$8,500.00` (10,000 - 1,500). Holdings table shows `AAPL: 10 shares`. |
| 8. | Navigate to "History". | A new `BUY` transaction for `AAPL` is recorded (Total $1,500.00). |
**Post-Condition**: Cash: **$8,500.00**. Holdings: **10 AAPL**.

#### 3.2 Successful Share Sale (AC-2)
**Priority**: Critical
**Objective**: Verify that a SELL transaction correctly increases cash and decreases holdings. (AAPL Price: $160.00).
**Starting State**: Trade Tab, Cash Balance: $8,500.00. Holdings: 10 AAPL.

| Step | Action | Expected Outcome |
| :--- | :----- | :--------------- |
| 1. | Navigate to the "Trade" tab. | Form is ready. |
| 2. | Select Action: `SELL`. | Dropdown displays `SELL`. |
| 3. | Enter Stock Symbol: `AAPL`. | Input accepted. |
| 4. | Enter Quantity: `5`. | Input accepted. (Total revenue: 5 * $160.00 = $800.00). |
| 5. | Click the "Execute Trade" button. | Transaction processes successfully. |
| 6. | Verify the Status message. | Status displays: "Success: Sold 5 shares of AAPL at $160.00 each for a total of $800.00." |
| 7. | Navigate to the "Portfolio" tab and refresh. | Cash Balance updates to `$9,300.00` (8,500 + 800). Holdings table shows `AAPL: 5 shares`. |
| 8. | Navigate to "History". | A new `SELL` transaction for `AAPL` is recorded (Total $800.00). |
**Post-Condition**: Cash: **$9,300.00**. Holdings: **5 AAPL**.

#### 3.3 Attempt to Buy with Insufficient Funds (AC-3)
**Priority**: Critical
**Objective**: Ensure the system prevents transactions that deplete cash below zero. (TSLA Price: $300.00).
**Starting State**: Trade Tab, Cash Balance: $9,300.00.

| Step | Action | Calculation | Expected Outcome |
| :--- | :----- | :---------- | :--------------- |
| 1. | Configure a BUY order for 32 shares of TSLA. | Cost: 32 * $300.00 = $9,600.00 (Required: $9,600.00; Available: $9,300.00) | Form fields populated. |
| 2. | Click the "Execute Trade" button. | Transaction rejected due to insufficient funds. |
| 3. | Verify the Status message. | Status displays: "Error: Insufficient funds. You need $9,600.00 to buy 32 shares of TSLA, but you only have $9,300.00." |
| 4. | Verify Cash Balance and Holdings (Portfolio tab). | Cash Balance remains `$9,300.00`. Holdings remain **5 AAPL**. |

#### 3.4 Attempt to Sell More Shares Than Owned (AC-4)
**Priority**: Critical
**Objective**: Ensure the system prevents short selling (selling shares not owned).
**Starting State**: Trade Tab, Holdings: 5 AAPL.

| Step | Action | Calculation | Expected Outcome |
| :--- | :----- | :---------- | :--------------- |
| 1. | Configure a SELL order for 6 shares of AAPL. | Selling 6 shares (Owned: 5 shares). | Form fields populated. |
| 2. | Click the "Execute Trade" button. | Transaction rejected due to insufficient shares. |
| 3. | Verify the Status message. | Status displays: "Error: Insufficient shares. You cannot sell 6 shares of AAPL as you only own 5." |
| 4. | Verify Holdings (Portfolio tab). | Holdings remain **5 AAPL**. |

#### 3.5 Invalid Input Validation (AC-5, AC-6)
**Priority**: High
**Objective**: Verify validation for symbol and quantity inputs.
**Starting State**: Trade Tab.

| Step | Action | Input | Expected Outcome |
| :--- | :----- | :---- | :--------------- |
| 1. | Attempt BUY with Invalid Symbol. | Symbol: `XYZ`, Quantity: 1 | Status displays: "Error: Invalid stock symbol 'XYZ'. Please use a valid symbol (e.g., AAPL, TSLA, GOOGL)." |
| 2. | Attempt BUY with zero quantity. | Symbol: `AAPL`, Quantity: 0 | Status displays: "Error: Quantity must be a positive whole number." |
| 3. | Attempt BUY with negative quantity. | Symbol: `AAPL`, Quantity: -5 | Status displays: "Error: Quantity must be a positive whole number." |
| 4. | Attempt BUY with fractional quantity. | Symbol: `AAPL`, Quantity: 2.5 | Status displays: "Error: Quantity must be a positive whole number." (Requires the system to reject non-integer input despite Gradio `precision=0` setting). |

#### 3.6 Non-Functional Test: Handle External Pricing API Failure
**Priority**: Medium
**Objective**: Ensure robust error handling when `get_share_price` fails.
**Starting State**: Trade Tab. (Assume the test environment can simulate an API timeout or error response for price retrieval).

| Step | Action | Expected Outcome |
| :--- | :----- | :--------------- |
| 1. | Configure a BUY order (AAPL, 10 shares). | Inputs ready. |
| 2. | **(Simulate)** The system receives a failure/null response from `get_share_price('AAPL')`. | Trade execution logic intercepts the failure. |
| 3. | Click the "Execute Trade" button. | Transaction is rejected. |
| 4. | Verify the Status message. | Status displays: "Error: Could not retrieve share price. Please try again later." |
| 5. | Verify Cash/Holdings. | Cash balance and holdings remain unchanged. |

---
### Epic 4: Portfolio and History View (US-004)

**Prerequisite Setup**: User `traderQA` has the following state established from previous successful scenarios:
*   Initial Deposit: $10,000.00
*   Transaction History: Initial Deposit (+$10k), Deposit (+$2k), Withdrawal (-$1.5k), Buy 10 AAPL (-$1.5k), Sell 5 AAPL (+$800).
*   **Net Deposits**: $12,000 - $1,500 = **$10,500.00**
*   **Current Cash Balance**: **$9,300.00**
*   **Holdings**: 5 shares of AAPL.

#### 4.1 Portfolio Calculation Verification (AC-1)
**Priority**: Critical
**Objective**: Validate the complex financial calculations using the glossary formulas.
**Assumed Current Prices**: AAPL: $170.00, TSLA: $300.00 (for comparison).

| Step | Action | Calculation/Expected Value | Expected Outcome |
| :--- | :----- | :------------------------- | :--------------- |
| 1. | Navigate to the "Portfolio" tab. | Current Prices (Simulated): AAPL: $170.00 | Portfolio view loads. |
| 2. | Click the "Refresh" button. | Triggers price retrieval and recalculation. | UI updates within the required 1 second performance window. |
| 3. | Verify Current Holdings table content. | Displays: Symbol: `AAPL`, Quantity: `5`, Current Price: `$170.00`, Total Value: `$850.00`. | Table displays data correctly. |
| 4. | Verify Cash Balance. | Expected: `$9,300.00` | Textbox displays: `$9,300.00`. |
| 5. | Verify Total Portfolio Value. | Cash ($9,300) + Shares ($850) = **$10,150.00** | Textbox displays: `$10,150.00`. |
| 6. | Verify Total Profit/Loss (P/L). | Total Portfolio Value ($10,150) - Net Deposits ($10,500) = **-$350.00** | Textbox displays: `-$350.00` (Negative P/L format verified). |

#### 4.2 Transaction History Audit (AC-2)
**Priority**: High
**Objective**: Ensure all transactions are accurately recorded and displayed in the correct order.
**Starting State**: Account with 5 total transactions (as established above).

| Step | Action | Expected Outcome |
| :--- | :----- | :--------------- |
| 1. | Navigate to the "History" tab. | Transaction History table loads (Snapshot US-004 - History View). |
| 2. | Verify the total number of entries. | 5 transactions should be displayed. |
| 3. | Verify the order of transactions. | The entries must be in reverse chronological order (SELL AAPL must be the top entry). |
| 4. | Verify data structure for all entries. | Check that all columns (Timestamp, Type, Symbol, Quantity, Price, Total) are populated correctly based on the transaction type (e.g., DEPOSIT/WITHDRAWAL should have 'N/A' or 'null' for Symbol/Price/Quantity; BUY/SELL must have all fields populated). |
| 5. | Audit specific SELL entry (3.2). | Type: `SELL`, Symbol: `AAPL`, Quantity: `5`, Price: `$160.00`, Total: `$800.00`. |

#### 4.3 Empty Portfolio Edge Case (AC-3)
**Priority**: Medium
**Objective**: Verify the portfolio state immediately after account creation before any trading activity.
**Starting State**: Use a *fresh* test account (e.g., `trader002`) initialized with $5,000.

| Step | Action | Expected Outcome |
| :--- | :----- | :--------------- |
| 1. | Create new account `trader002` with deposit `$5000.00`. | Account created successfully. Net Deposits: $5,000.00. |
| 2. | Navigate to the "Portfolio" tab. | Portfolio view loads. |
| 3. | Verify Holdings table. | The table is empty, or displays the message: "You do not own any shares." |
| 4. | Verify Portfolio Value and P/L. | Total Portfolio Value: `$5,000.00`. Total Profit / Loss: `$0.00`. |
| 5. | Navigate to the "History" tab. | Only one DEPOSIT transaction for `$5,000.00` is listed. |

#### 4.4 Non-Functional Test: Data Integrity and Performance
**Priority**: High
**Objective**: Verify that rapid transactions are correctly handled (Data Integrity) and that the Portfolio Refresh meets performance requirements.
**Starting State**: `traderQA` established state (Post 4.1).

| Step | Action | Expected Outcome |
| :--- | :----- | :--------------- |
| 1. | **(Performance)** Click the "Refresh" button on the Portfolio tab. | The entire screen update (price fetch + calculation + display) completes within 1 second. |
| 2. | **(Integrity)** Simulate concurrent high-frequency deposits/withdrawals (e.g., 10 transactions executed rapidly). | No race conditions occur; the final cash balance is mathematically correct based on the sequence of operations. |
| 3. | **(Scalability)** If possible, load 1,000 dummy transactions into the history. | The History table displays without significant UI lag or freezing, confirming the scalability requirement. |