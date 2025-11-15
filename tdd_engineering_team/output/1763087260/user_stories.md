### **Project: Simple Trading Simulation Platform - Account Management**

This document outlines the user stories required to build the core features of the trading simulation platform's account management system. Each story is designed to be developer-ready, including detailed acceptance criteria, UI/UX specifications using the Gradio framework, and explicit user-facing messages.

---

### **Epic: Portfolio Management**

**Description:** Provide users with the fundamental tools to manage their trading account, execute trades, and monitor their portfolio's performance.

---

### **User Story 1: View Portfolio Dashboard**

*   **ID:** T-01
*   **Title:** User can view their portfolio dashboard with key metrics.
*   **User Story:** As a trader, I want to see a clear and concise dashboard with my cash balance, total portfolio value, and overall profit/loss, so that I can quickly assess my financial standing at a glance.
*   **Business Value:** This is the central hub for the user, providing immediate feedback on their performance and financial status. It's essential for user engagement and decision-making.
*   **Priority:** Highest

#### **Acceptance Criteria (AC)**

*   **AC-1.1 (Initial State):**
    *   **Given** a new user account is initialized (e.g., with a $10,000 starting deposit)
    *   **When** the user loads the application
    *   **Then** the dashboard should display:
        *   Cash Balance: $10,000.00
        *   Portfolio Value: $0.00
        *   Total Value (Cash + Portfolio): $10,000.00
        *   Profit / Loss: $0.00
*   **AC-1.2 (Portfolio Value Calculation):**
    *   **Given** the user owns 10 shares of AAPL and 5 shares of TSLA
    *   **And** the `get_share_price('AAPL')` function returns 150.00
    *   **And** the `get_share_price('TSLA')` function returns 200.00
    *   **When** the dashboard view is rendered
    *   **Then** the "Portfolio Value" should be calculated and displayed as (10 * 150) + (5 * 200) = $2,500.00.
*   **AC-1.3 (Profit/Loss Calculation):**
    *   **Given** the user started with an initial deposit of $10,000
    *   **And** their current "Total Value" (Cash + Portfolio) is $12,500.00
    *   **When** the dashboard view is rendered
    *   **Then** the "Profit / Loss" should be displayed as $2,500.00.
*   **AC-1.4 (Real-time Update After Transaction):**
    *   **Given** the user is on the dashboard view
    *   **When** the user successfully completes any transaction (deposit, withdraw, buy, or sell)
    *   **Then** all dashboard metrics (Cash, Portfolio Value, Total Value, P/L) must immediately refresh to reflect the new state.

#### **UI/UX Specifications (Gradio)**

*   **Layout:** A top-level section with key metrics displayed prominently.
*   **Wireframe:**
    ```
    -----------------------------------------------------------------
    # Trading Simulation Platform

    ## Portfolio Overview
    [gr.Markdown]

    [gr.Blocks]
      [gr.Row]
        [gr.Number label="Cash Balance", value="$10,000.00", interactive=False]
        [gr.Number label="Portfolio Value", value="$0.00", interactive=False]
      [/gr.Row]
      [gr.Row]
        [gr.Number label="Total Value", value="$10,000.00", interactive=False]
        [gr.Number label="Profit / Loss", value="$0.00", interactive=False]
      [/gr.Row]
    [/gr.Blocks]
    -----------------------------------------------------------------
    ```
*   **User Messages:**
    *   **Success Messages:** Not applicable for this view-only story.
    *   **Error Messages:** Not applicable for this view-only story.

#### **Out of Scope**
*   User account creation/login (assume a single, pre-initialized user).
*   Real-time, automatic updates of share prices. The dashboard only updates on user action.

---

### **User Story 2: Manage Funds**

*   **ID:** T-02
*   **Title:** User can deposit and withdraw cash from their account.
*   **User Story:** As a trader, I want to deposit and withdraw cash, so that I can manage my account's liquidity for trading or taking profits.
*   **Business Value:** Core functionality for managing the cash component of the portfolio. Enables users to start trading and realize gains.
*   **Priority:** High

#### **Acceptance Criteria (AC)**

*   **AC-2.1 (Successful Deposit):**
    *   **Given** the user has a cash balance of $5,000
    *   **When** the user enters "1000" in the deposit field and clicks "Deposit"
    *   **Then** the system should update the cash balance to $6,000
    *   **And** a success message "Successfully deposited $1,000.00. New cash balance is $6,000.00." is displayed.
*   **AC-2.2 (Successful Withdrawal):**
    *   **Given** the user has a cash balance of $5,000
    *   **When** the user enters "500" in the withdrawal field and clicks "Withdraw"
    *   **Then** the system should update the cash balance to $4,500
    *   **And** a success message "Successfully withdrew $500.00. New cash balance is $4,500.00." is displayed.
*   **AC-2.3 (Error on Invalid Deposit Amount):**
    *   **Given** the user is on the fund management screen
    *   **When** the user enters "-100" or "0" in the deposit field and clicks "Deposit"
    *   **Then** the cash balance should not change
    *   **And** an error message "Error: Deposit amount must be a positive number." is displayed.
*   **AC-2.4 (Error on Insufficient Funds for Withdrawal):**
    *   **Given** the user has a cash balance of $500
    *   **When** the user enters "501" in the withdrawal field and clicks "Withdraw"
    *   **Then** the cash balance should not change
    *   **And** an error message "Error: Insufficient funds. Cannot withdraw $501.00 from a balance of $500.00." is displayed.
*   **AC-2.5 (Error on Invalid Withdrawal Amount):**
    *   **Given** the user is on the fund management screen
    *   **When** the user enters "-100" or "0" in the withdrawal field and clicks "Withdraw"
    *   **Then** the cash balance should not change
    *   **And** an error message "Error: Withdrawal amount must be a positive number." is displayed.

#### **UI/UX Specifications (Gradio)**

*   **Layout:** A dedicated section or tab for fund management with input fields and buttons for depositing and withdrawing. A single message area will show feedback.
*   **Wireframe:**
    ```
    -----------------------------------------------------------------
    ### Manage Funds
    [gr.Markdown]

    [gr.Textbox label="Action Status", value="", interactive=False]  <-- For Success/Error messages

    [gr.Row]
      [gr.Number label="Amount ($)", placeholder="e.g., 1000"]
      [gr.Button value="Deposit"]
      [gr.Button value="Withdraw"]
    [/gr.Row]
    -----------------------------------------------------------------
    ```
*   **User Messages:**
    *   **Success Messages:**
        *   `Successfully deposited ${amount}. New cash balance is ${new_balance}.`
        *   `Successfully withdrew ${amount}. New cash balance is ${new_balance}.`
    *   **Error Messages:**
        *   `Error: Deposit amount must be a positive number.`
        *   `Error: Withdrawal amount must be a positive number.`
        *   `Error: Insufficient funds. Cannot withdraw ${amount} from a balance of ${current_balance}.`
        *   `Error: Please enter a valid numerical amount.`

#### **Out of Scope**
*   Connection to real bank accounts or payment processors.

---

### **User Story 3: Execute Trades**

*   **ID:** T-03
*   **Title:** User can buy and sell shares.
*   **User Story:** As a trader, I want to buy and sell shares of available stocks, so that I can execute my investment strategy.
*   **Business Value:** This is the primary interaction of the simulation. It allows users to actively participate in the market and change their portfolio composition.
*   **Priority:** Highest

#### **Acceptance Criteria (AC)**

*   **AC-3.1 (Successful Buy):**
    *   **Given** the user has a cash balance of $10,000 and owns 0 shares of AAPL
    *   **And** the current price of AAPL is $150.00
    *   **When** the user enters "AAPL" for the symbol, "10" for the quantity, and clicks "Buy"
    *   **Then** the user's cash balance should decrease by $1,500 to $8,500
    *   **And** the user's holdings should show 10 shares of AAPL
    *   **And** a success message "Success: Bought 10 shares of AAPL at $150.00 each for a total of $1,500.00." is displayed.
*   **AC-3.2 (Successful Sell):**
    *   **Given** the user has a cash balance of $8,500 and owns 10 shares of AAPL
    *   **And** the current price of AAPL is $160.00
    *   **When** the user enters "AAPL" for the symbol, "5" for the quantity, and clicks "Sell"
    *   **Then** the user's cash balance should increase by $800 to $9,300
    *   **And** the user's holdings should show 5 shares of AAPL
    *   **And** a success message "Success: Sold 5 shares of AAPL at $160.00 each for a total of $800.00." is displayed.
*   **AC-3.3 (Error on Insufficient Funds for Buy):**
    *   **Given** the user has a cash balance of $1,000
    *   **And** the current price of AAPL is $150.00
    *   **When** the user tries to buy 10 shares of AAPL (total cost $1,500)
    *   **Then** the transaction is rejected, and cash/holdings remain unchanged
    *   **And** an error message "Error: Insufficient funds. You need $1,500.00 to buy, but you only have $1,000.00." is displayed.
*   **AC-3.4 (Error on Selling Unowned Shares):**
    *   **Given** the user owns 0 shares of GOOGL
    *   **When** the user tries to sell 5 shares of GOOGL
    *   **Then** the transaction is rejected, and cash/holdings remain unchanged
    *   **And** an error message "Error: Cannot sell. You do not own any shares of GOOGL." is displayed.
*   **AC-3.5 (Error on Selling More Shares Than Owned):**
    *   **Given** the user owns 10 shares of TSLA
    *   **When** the user tries to sell 11 shares of TSLA
    *   **Then** the transaction is rejected, and cash/holdings remain unchanged
    *   **And** an error message "Error: Cannot sell 11 shares of TSLA. You only own 10." is displayed.
*   **AC-3.6 (Error on Invalid Symbol):**
    *   **Given** the `get_share_price` function returns an error/null for an invalid symbol
    *   **When** the user tries to buy or sell a symbol like "INVALID"
    *   **Then** the transaction is rejected
    *   **And** an error message "Error: Ticker symbol 'INVALID' not found." is displayed.
*   **AC-3.7 (Error on Non-Positive Quantity):**
    *   **Given** the user is on the trade execution screen
    *   **When** the user enters "0" or "-5" for quantity and clicks "Buy" or "Sell"
    *   **Then** the transaction is rejected
    *   **And** an error message "Error: Quantity must be a positive whole number." is displayed.

#### **UI/UX Specifications (Gradio)**

*   **Layout:** A dedicated section for trade execution.
*   **Wireframe:**
    ```
    -----------------------------------------------------------------
    ### Execute Trade
    [gr.Markdown]

    [gr.Textbox label="Action Status", value="", interactive=False]  <-- For Success/Error messages

    [gr.Row]
      [gr.Dropdown label="Symbol", choices=["AAPL", "TSLA", "GOOGL"]]
      [gr.Number label="Quantity", precision=0]  <-- precision=0 for whole shares
    [/gr.Row]
    [gr.Row]
      [gr.Button value="Buy"]
      [gr.Button value="Sell"]
    [/gr.Row]
    -----------------------------------------------------------------
    ```
*   **User Messages:**
    *   **Success Messages:**
        *   `Success: Bought {quantity} shares of {symbol} at ${price} each for a total of ${total_cost}.`
        *   `Success: Sold {quantity} shares of {symbol} at ${price} each for a total of ${total_value}.`
    *   **Error Messages:**
        *   `Error: Insufficient funds. You need ${required_cash} to buy, but you only have ${current_cash}.`
        *   `Error: Cannot sell. You do not own any shares of {symbol}.`
        *   `Error: Cannot sell {quantity} shares of {symbol}. You only own {owned_quantity}.`
        *   `Error: Ticker symbol '{symbol}' not found.`
        *   `Error: Quantity must be a positive whole number.`

#### **Non-Functional Requirements**
*   The `get_share_price(symbol)` API call should complete within 500ms to ensure the UI remains responsive during trade validation.

#### **Out of Scope**
*   Different order types (e.g., limit, stop-loss). All trades are market orders.
*   Trading fractional shares.

---

### **User Story 4: View Holdings and Transaction History**

*   **ID:** T-04
*   **Title:** User can view their detailed holdings and a list of all transactions.
*   **User Story:** As a trader, I want to see a detailed breakdown of my current stock holdings and a chronological history of all my transactions, so that I can analyze my portfolio composition and review my past activity.
*   **Business Value:** Provides transparency and detailed information, allowing users to track their decisions and understand their portfolio's structure.
*   **Priority:** High

#### **Acceptance Criteria (AC)**

*   **AC-4.1 (Display Current Holdings):**
    *   **Given** the user owns 10 shares of AAPL and 5 shares of TSLA
    *   **And** the current price of AAPL is $150 and TSLA is $200
    *   **When** the user views the "Current Holdings" tab
    *   **Then** a table/dataframe is displayed with rows:
        *   `| Symbol | Quantity | Current Price | Total Value |`
        *   `| AAPL   | 10       | $150.00       | $1,500.00   |`
        *   `| TSLA   | 5        | $200.00       | $1,000.00   |`
*   **AC-4.2 (Display Empty Holdings):**
    *   **Given** the user owns no shares
    *   **When** the user views the "Current Holdings" tab
    *   **Then** a message "You do not currently hold any shares." is displayed instead of a table.
*   **AC-4.3 (Display Transaction History):**
    *   **Given** the user has performed the following actions in order:
        1.  Initial Deposit of $10,000
        2.  Bought 10 AAPL
        3.  Sold 5 AAPL
        4.  Withdrew $500
    *   **When** the user views the "Transaction History" tab
    *   **Then** a table/dataframe is displayed with the transactions in reverse chronological order (most recent first):
        *   `| Timestamp           | Type     | Details                                    |`
        *   `| 2023-10-27 10:05:00 | Withdraw | Amount: $500.00                            |`
        *   `| 2023-10-27 10:04:00 | Sell     | 5 shares of AAPL @ $160.00 ea.             |`
        *   `| 2023-10-27 10:02:00 | Buy      | 10 shares of AAPL @ $150.00 ea.            |`
        *   `| 2023-10-27 10:00:00 | Deposit  | Initial Deposit: $10,000.00                |`
*   **AC-4.4 (Display Empty Transaction History):**
    *   **Given** the user has made no transactions other than the initial deposit
    *   **When** the user views the "Transaction History" tab
    *   **Then** only the initial deposit transaction is shown. If no initial transaction exists, a message "No transactions have been recorded yet." is displayed.

#### **UI/UX Specifications (Gradio)**

*   **Layout:** A tabbed interface to switch between Holdings and Transaction History.
*   **Wireframe:**
    ```
    -----------------------------------------------------------------
    [gr.Tabs]
      [gr.Tab label="Current Holdings"]
        [gr.DataFrame headers=["Symbol", "Quantity", "Current Price", "Total Value"]]
        // or //
        [gr.Markdown value="You do not currently hold any shares."]

      [/gr.Tab]
      [gr.Tab label="Transaction History"]
        [gr.DataFrame headers=["Timestamp", "Type", "Details"]]
        // or //
        [gr.Markdown value="No transactions have been recorded yet."]
      [/gr.Tab]
    [/gr.Tabs]
    -----------------------------------------------------------------
    ```
*   **User Messages:**
    *   **Success Messages:** Not applicable (data display).
    *   **Error Messages:** Not applicable (data display).
    *   **Informational Messages:**
        *   `You do not currently hold any shares.`
        *   `No transactions have been recorded yet.`

#### **Out of Scope**
*   Filtering or searching transaction history.
*   Exporting data to CSV/Excel.