### **Epic: Trading Simulation Account Management**

This epic covers the foundational features for a single-user trading simulation platform. The goal is to provide core functionality for managing cash, executing trades, and viewing portfolio performance in a simple prototype UI built with Gradio.

---

### **User Story: TRD-001 - Deposit Cash into Account**

*   **ID:** TRD-001
*   **Title:** Deposit Cash into Account
*   **User Story:** As a user, I want to deposit funds into my account so that I have capital to start trading.
*   **Business Value:** Enables the primary user journey. Without funds, no trading can occur. This is the entry point for all other platform activities.
*   **Priority:** High

#### **Acceptance Criteria (Gherkin Format)**

**Scenario 1: Successful Deposit**
*   **Given** my current cash balance is $1,000.00
*   **When** I enter "500" into the deposit amount field and click "Deposit"
*   **Then** my new cash balance becomes $1,500.00
*   **And** a success message "Success: Deposited $500.00. Your new cash balance is $1,500.00." is displayed in the UI.
*   **And** a "DEPOSIT" transaction for $500.00 is added to my transaction history.

**Scenario 2: Attempting to Deposit a Negative Amount**
*   **Given** my current cash balance is $1,000.00
*   **When** I enter "-100" into the deposit amount field and click "Deposit"
*   **Then** my cash balance remains $1,000.00
*   **And** an error message "Error: Deposit amount must be a positive number." is displayed in the UI.
*   **And** no transaction is recorded.

**Scenario 3: Attempting to Deposit a Zero Amount**
*   **Given** my current cash balance is $1,000.00
*   **When** I enter "0" into the deposit amount field and click "Deposit"
*   **Then** my cash balance remains $1,000.00
*   **And** an error message "Error: Deposit amount must be a positive number." is displayed in the UI.
*   **And** no transaction is recorded.

**Scenario 4: Attempting to Deposit Non-Numeric Text**
*   **Given** my account exists
*   **When** I enter "one hundred" into the deposit amount field and click "Deposit"
*   **Then** my cash balance does not change
*   **And** an error message "Error: Please enter a valid numerical amount for the deposit." is displayed in the UI.

#### **UI/UX Specifications**

*   **Framework:** Gradio
*   **Layout:** A `gr.Group` or `gr.Column` for cash management actions.
*   **Components:**
    *   `gr.Number(label="Deposit Amount")`: Input field for the user to enter the amount to deposit.
    *   `gr.Button(value="Deposit")`: A button to trigger the deposit action.
    *   `gr.Textbox(label="Status Message", interactive=False)`: A non-editable textbox to display success or error messages from the last action.
    *   `gr.Textbox(label="Current Cash Balance", interactive=False)`: A non-editable textbox that always displays the current cash balance, updated after every successful transaction.

#### **Out of Scope**
*   Integration with real payment gateways (e.g., Stripe, PayPal).
*   Handling different currencies.
*   Deposit limits or fees.

---

### **User Story: TRD-002 - Withdraw Cash from Account**

*   **ID:** TRD-002
*   **Title:** Withdraw Cash from Account
*   **User Story:** As a user, I want to withdraw available funds from my account so that I can realize my cash gains.
*   **Business Value:** Allows users to complete the investment cycle by taking cash out of the simulation.
*   **Priority:** High

#### **Acceptance Criteria (Gherkin Format)**

**Scenario 1: Successful Withdrawal**
*   **Given** my current cash balance is $2,000.00
*   **When** I enter "500" into the withdrawal amount field and click "Withdraw"
*   **Then** my new cash balance becomes $1,500.00
*   **And** a success message "Success: Withdrew $500.00. Your new cash balance is $1,500.00." is displayed.
*   **And** a "WITHDRAW" transaction for $500.00 is added to my transaction history.

**Scenario 2: Attempting to Withdraw More Funds Than Available**
*   **Given** my current cash balance is $2,000.00
*   **When** I enter "2500" into the withdrawal amount field and click "Withdraw"
*   **Then** my cash balance remains $2,000.00
*   **And** an error message "Error: Withdrawal failed. Insufficient funds. You tried to withdraw $2,500.00 but only have $2,000.00 available." is displayed.
*   **And** no transaction is recorded.

**Scenario 3: Attempting to Withdraw a Negative or Zero Amount**
*   **Given** my current cash balance is $2,000.00
*   **When** I enter "-100" into the withdrawal amount field and click "Withdraw"
*   **Then** my cash balance remains $2,000.00
*   **And** an error message "Error: Withdrawal amount must be a positive number." is displayed.

#### **UI/UX Specifications**

*   **Framework:** Gradio
*   **Layout:** Placed within the same cash management group as the Deposit feature.
*   **Components:**
    *   `gr.Number(label="Withdraw Amount")`: Input field for the withdrawal amount.
    *   `gr.Button(value="Withdraw")`: Button to trigger the withdrawal action.
    *   Uses the same shared `gr.Textbox(label="Status Message")` and `gr.Textbox(label="Current Cash Balance")` as the Deposit story.

#### **Out of Scope**
*   Integration with real bank accounts.
*   Withdrawal processing times or holds.
*   Withdrawal fees.

---

### **User Story: TRD-003 - Buy Shares of a Stock**

*   **ID:** TRD-003
*   **Title:** Buy Shares of a Stock
*   **User Story:** As a user, I want to buy shares of a specific stock so that I can build my investment portfolio.
*   **Business Value:** This is the core investment action, allowing users to actively participate in the simulation.
*   **Priority:** High

#### **Acceptance Criteria (Gherkin Format)**

**Scenario 1: Successful Share Purchase**
*   **Given** I have a cash balance of $10,000.00 and 0 shares of "AAPL"
*   **And** the current price of "AAPL" is $150.00 per share
*   **When** I select "AAPL", enter quantity "10", and click "Buy"
*   **Then** my cash balance is reduced to $8,500.00 (10,000 - 10 * 150)
*   **And** my holdings now include 10 shares of "AAPL"
*   **And** a success message "Success: Bought 10 shares of AAPL at $150.00 each for a total of $1,500.00. New cash balance: $8,500.00." is displayed.
*   **And** a "BUY" transaction is added to my history.

**Scenario 2: Insufficient Funds for Purchase**
*   **Given** I have a cash balance of $1,000.00
*   **And** the current price of "TSLA" is $200.00 per share
*   **When** I select "TSLA", enter quantity "6", and click "Buy"
*   **Then** my cash balance remains $1,000.00
*   **And** my holdings of "TSLA" do not change
*   **And** an error message "Error: Purchase failed. Insufficient funds. Cost is $1,200.00 but you only have $1,000.00." is displayed.

**Scenario 3: Attempt to Buy with an Invalid Quantity**
*   **Given** I have sufficient cash
*   **When** I select "GOOGL", enter quantity "-5", and click "Buy"
*   **Then** my cash balance and holdings do not change
*   **And** an error message "Error: Quantity must be a positive number." is displayed.

**Scenario 4: API Failure for Share Price**
*   **Given** the `get_share_price('INVALID')` function will fail or return an error
*   **When** I enter the symbol "INVALID", a valid quantity, and click "Buy"
*   **Then** my cash balance and holdings do not change
*   **And** an error message "Error: Invalid stock symbol 'INVALID'. Could not retrieve price." is displayed.

#### **UI/UX Specifications**

*   **Framework:** Gradio
*   **Layout:** A dedicated `gr.Group` or `gr.Column` for Trading Actions.
*   **Components:**
    *   `gr.Dropdown(label="Stock Symbol", choices=['AAPL', 'TSLA', 'GOOGL'])`: A dropdown to select the stock.
    *   `gr.Number(label="Quantity", precision=0)`: Input for the number of shares (whole numbers only).
    *   `gr.Button(value="Buy")`: Button to execute the buy order.
    *   `gr.Button(value="Sell")`: Button for the sell order (see TRD-004).
    *   Uses the same shared `gr.Textbox(label="Status Message")`.

#### **Out of Scope**
*   Market, limit, or stop orders.
*   Trading fees or commissions.
*   Real-time price feeds (uses the fixed-price `get_share_price` function).
*   Searching for stocks not in the pre-defined list.

---

### **User Story: TRD-004 - Sell Shares of a Stock**

*   **ID:** TRD-004
*   **Title:** Sell Shares of a Stock
*   **User Story:** As a user, I want to sell shares of a stock I own so that I can lock in profits or cut losses.
*   **Business Value:** Complements the "Buy" action, allowing users to manage their portfolio and realize gains or losses.
*   **Priority:** High

#### **Acceptance Criteria (Gherkin Format)**

**Scenario 1: Successful Share Sale**
*   **Given** I have a cash balance of $5,000.00 and own 20 shares of "TSLA"
*   **And** the current price of "TSLA" is $200.00 per share
*   **When** I select "TSLA", enter quantity "10", and click "Sell"
*   **Then** my cash balance is increased to $7,000.00 (5,000 + 10 * 200)
*   **And** my holdings of "TSLA" are reduced to 10 shares
*   **And** a success message "Success: Sold 10 shares of TSLA at $200.00 each for a total of $2,000.00. New cash balance: $7,000.00." is displayed.
*   **And** a "SELL" transaction is added to my history.

**Scenario 2: Attempting to Sell More Shares Than Owned**
*   **Given** I own 20 shares of "TSLA"
*   **When** I select "TSLA", enter quantity "25", and click "Sell"
*   **Then** my cash balance and TSLA holdings do not change
*   **And** an error message "Error: Sale failed. You do not own enough shares. You tried to sell 25 of TSLA but you only own 20." is displayed.

**Scenario 3: Attempting to Sell Shares Not Owned at All**
*   **Given** I own 0 shares of "GOOGL"
*   **When** I select "GOOGL", enter quantity "5", and click "Sell"
*   **Then** my cash balance and GOOGL holdings do not change
*   **And** an error message "Error: Sale failed. You do not own enough shares. You tried to sell 5 of GOOGL but you only own 0." is displayed.

**Scenario 4: Attempt to Sell with an Invalid Quantity**
*   **Given** I own sufficient shares
*   **When** I select "AAPL", enter quantity "0", and click "Sell"
*   **Then** my cash balance and holdings do not change
*   **And** an error message "Error: Quantity must be a positive number." is displayed.

#### **UI/UX Specifications**

*   **Framework:** Gradio
*   **Layout:** Uses the same Trading Actions group as the Buy feature.
*   **Components:**
    *   Uses the same `gr.Dropdown` and `gr.Number` components as the Buy story.
    *   `gr.Button(value="Sell")`: Button to execute the sell order.
    *   Uses the same shared `gr.Textbox(label="Status Message")`.

#### **Out of Scope**
*   Short selling (this is explicitly prevented by the business logic).
*   Tax implications of selling (e.g., capital gains).

---

### **User Story: TRD-005 - View Portfolio Summary**

*   **ID:** TRD-005
*   **Title:** View Portfolio Summary
*   **User Story:** As a user, I want to view a summary of my portfolio so that I can understand my current financial position at a glance.
*   **Business Value:** Provides critical visibility into performance, enabling informed decisions for future trades.
*   **Priority:** Medium

#### **Acceptance Criteria (Gherkin Format)**

**Scenario 1: Viewing a Populated Portfolio**
*   **Given** I have performed the following actions in order:
    1.  Deposited $10,000.00
    2.  Bought 10 shares of "AAPL" at $150.00
    3.  Bought 5 shares of "TSLA" at $180.00
*   **And** the current prices are: "AAPL" at $160.00, "TSLA" at $200.00
*   **When** I view the Portfolio Summary section of the UI
*   **Then** the following information is displayed accurately:
    *   **Cash Balance:** $7,600.00 (10000 - 1500 - 900)
    *   **Holdings Table:**
        | Symbol | Quantity | Current Price | Market Value |
        |--------|----------|---------------|--------------|
        | AAPL   | 10       | $160.00       | $1,600.00    |
        | TSLA   | 5        | $200.00       | $1,000.00    |
    *   **Total Portfolio Value:** $10,200.00 (7600 cash + 1600 AAPL + 1000 TSLA)
    *   **Total Profit/Loss:** +$200.00 (10200 current value - 10000 total deposited)
*   **And** this summary automatically updates after any new transaction (buy, sell, deposit, withdraw).

**Scenario 2: Viewing an Empty Portfolio**
*   **Given** I have just started and have a cash balance of $0.00 and no holdings
*   **When** I view the Portfolio Summary
*   **Then** the UI displays:
    *   **Cash Balance:** $0.00
    *   **Holdings Table:** Is empty or shows a message like "You have no holdings."
    *   **Total Portfolio Value:** $0.00
    *   **Total Profit/Loss:** $0.00

#### **UI/UX Specifications**

*   **Framework:** Gradio
*   **Layout:** A dedicated `gr.Column` or `gr.Tab` for "Portfolio Summary". This should be always visible.
*   **Components:**
    *   `gr.Markdown("## Portfolio Summary")`: A title for the section.
    *   `gr.Textbox(label="Total Portfolio Value", interactive=False)`
    *   `gr.Textbox(label="Total Profit / Loss", interactive=False)`
    *   `gr.Textbox(label="Cash Balance", interactive=False)` (This can be the same component from the cash management section).
    *   `gr.Dataframe(headers=["Symbol", "Quantity", "Current Price", "Market Value"])`: A table to display the stock holdings.

#### **Out of Scope**
*   Graphical charts or historical performance data.
*   Advanced metrics (e.g., Sharpe ratio, Alpha).
*   Displaying daily P/L.

---

### **User Story: TRD-006 - View Transaction History**

*   **ID:** TRD-006
*   **Title:** View Transaction History
*   **User Story:** As a user, I want to view a list of all my past transactions so that I can review my trading activity.
*   **Business Value:** Provides an audit trail for the user, increasing transparency and trust in the simulation.
*   **Priority:** Medium

#### **Acceptance Criteria (Gherkin Format)**

**Scenario 1: Viewing a List of Transactions**
*   **Given** I have performed the following actions:
    1.  Deposited $5,000.00
    2.  Bought 10 "AAPL" at $150.00
    3.  Sold 5 "AAPL" at $160.00
*   **When** I navigate to the "Transaction History" view
*   **Then** I see a table displaying the transactions in reverse chronological order (most recent first)
*   **And** the table contains the following data:
    | Timestamp                 | Type    | Symbol | Quantity | Price per Share | Total Value |
    |---------------------------|---------|--------|----------|-----------------|-------------|
    | [Timestamp of Sale]       | SELL    | AAPL   | 5        | $160.00         | $800.00     |
    | [Timestamp of Purchase]   | BUY     | AAPL   | 10       | $150.00         | $1,500.00   |
    | [Timestamp of Deposit]    | DEPOSIT | -      | -        | -               | $5,000.00   |

#### **UI/UX Specifications**

*   **Framework:** Gradio
*   **Layout:** A separate `gr.Tab` or `gr.Accordion` section labeled "Transaction History".
*   **Components:**
    *   `gr.Dataframe(headers=["Timestamp", "Type", "Symbol", "Quantity", "Price per Share", "Total Value"])`: A table to display the complete transaction log. The `Timestamp` should be automatically generated by the system for each transaction.

#### **Out of Scope**
*   Filtering or searching transaction history.
*   Exporting transaction history to CSV/PDF.
*   Paginating the transaction list.