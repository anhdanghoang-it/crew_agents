### **Epic: Account & Portfolio Management System**

**Epic Description:** To provide users of the trading simulation platform with a comprehensive and intuitive system to manage their account funds, execute trades, and monitor their portfolio performance. This epic encompasses the full lifecycle of user interaction, from account creation and funding to trading and performance analysis.

**Business Goal:** Increase user engagement and platform adoption by providing a core, functional, and user-friendly simulation of a real-world trading account.

**User Stories in this Epic:**
*   **PORT-001:** Manage Account Funds (Deposit & Withdraw)
*   **PORT-002:** Execute Trades (Buy & Sell Shares)
*   **PORT-003:** View Portfolio Dashboard
*   **PORT-004:** View Transaction History

---

### **User Story: PORT-001**

**ID:** PORT-001
**Title:** Manage Account Funds (Deposit & Withdraw)
**User Story:** As a `platform user`, I want to `deposit and withdraw funds from my account` so that `I can manage my cash balance for trading`.
**Business Value:** Foundational capability. Users cannot trade without funds. This directly enables the core functionality of the platform.
**Priority:** High

---

#### **UI/UX Specifications**

**Framework:** Gradio

**Wireframe/Layout:** The functionality will be hosted within a dedicated tab named "Manage Funds".

```
+-------------------------------------------------------------------+
| [Portfolio Dashboard] [Execute Trade] [Manage Funds] [History]    |  <-- gr.Tabs
+-------------------------------------------------------------------+
|                                                                   |
|   Manage Your Funds                                               |  <-- gr.Markdown
|   -----------------                                               |
|                                                                   |
|   Current Cash Balance:  [ $10,000.00 ]                           |  <-- gr.Number (label="Current Cash Balance", interactive=False)
|                                                                   |
|   Amount:                [ 500.00      ]                           |  <-- gr.Number (label="Amount")
|                                                                   |
|   [   Deposit   ]  [  Withdraw   ]                                |  <-- gr.Button, gr.Button
|                                                                   |
|   +-------------------------------------------------------------+ |
|   | Status: Successfully deposited $500.00. New balance: ...    | |  <-- gr.Markdown (label="Status", initially hidden/empty)
|   +-------------------------------------------------------------+ |
|                                                                   |
+-------------------------------------------------------------------+
```

**Component Specifications:**
*   `gr.Tabs`: Main navigation for the application.
*   `gr.Tab(label="Manage Funds")`: Contains all components for this story.
*   `gr.Markdown("## Manage Your Funds")`: A clear title for the tab.
*   `gr.Number(label="Current Cash Balance", interactive=False)`: Displays the user's current cash. It cannot be edited by the user.
*   `gr.Number(label="Amount", minimum=0.01)`: A numeric input for the user to specify the transaction amount.
*   `gr.Button("Deposit")`: A button to trigger the deposit action.
*   `gr.Button("Withdraw")`: A button to trigger the withdrawal action.
*   `gr.Markdown(label="Status")`: A component to display all success and error messages. It should be visually distinct (e.g., green text for success, red for errors).

**Accessibility Checklist:**
*   [x] All input components (`gr.Number`) have clear, descriptive labels.
*   [x] All buttons (`gr.Button`) have clear, actionable text.
*   [x] Status messages are displayed in a dedicated, consistently located component.

---

#### **Success and Error Messages**

**Success Messages:**
1.  **Deposit:** "✅ Success: Successfully deposited ${amount}. Your new cash balance is ${new_balance}."
2.  **Withdrawal:** "✅ Success: Successfully withdrew ${amount}. Your new cash balance is ${new_balance}."

**Error Messages:**
1.  **Invalid Amount:** "❌ Error: Amount must be a positive number."
2.  **Insufficient Funds:** "❌ Error: Insufficient funds for withdrawal. Your current balance is ${current_balance}."
3.  **Null/Empty Input:** "❌ Error: Please enter an amount to deposit or withdraw."
4.  **Backend/API Failure:** "❌ Error: The transaction could not be completed due to a system error. Please try again later."

---

#### **Acceptance Criteria (Gherkin Format)**

**Scenario 1: Successful Deposit**
*   **Given** I am on the "Manage Funds" screen and my "Current Cash Balance" is `$1,000.00`.
*   **When** I enter `500` into the "Amount" field and click the "Deposit" button.
*   **Then** the "Current Cash Balance" display updates to `$1,500.00`.
*   **And** the "Status" message displays: "✅ Success: Successfully deposited $500.00. Your new cash balance is $1,500.00."

**Scenario 2: Successful Withdrawal**
*   **Given** I am on the "Manage Funds" screen and my "Current Cash Balance" is `$1,000.00`.
*   **When** I enter `200` into the "Amount" field and click the "Withdraw" button.
*   **Then** the "Current Cash Balance" display updates to `$800.00`.
*   **And** the "Status" message displays: "✅ Success: Successfully withdrew $200.00. Your new cash balance is $800.00."

**Scenario 3: Attempted Withdrawal with Insufficient Funds**
*   **Given** I am on the "Manage Funds" screen and my "Current Cash Balance" is `$100.00`.
*   **When** I enter `150` into the "Amount" field and click the "Withdraw" button.
*   **Then** the "Current Cash Balance" display remains `$100.00`.
*   **And** the "Status" message displays: "❌ Error: Insufficient funds for withdrawal. Your current balance is $100.00."

**Scenario 4: Attempted Transaction with a Negative Amount**
*   **Given** I am on the "Manage Funds" screen.
*   **When** I enter `-50` into the "Amount" field and click either "Deposit" or "Withdraw".
*   **Then** my "Current Cash Balance" does not change.
*   **And** the "Status" message displays: "❌ Error: Amount must be a positive number."

**Scenario 5: Attempted Transaction with a Zero Amount**
*   **Given** I am on the "Manage Funds" screen.
*   **When** I enter `0` into the "Amount" field and click either "Deposit" or "Withdraw".
*   **Then** my "Current Cash Balance" does not change.
*   **And** the "Status" message displays: "❌ Error: Amount must be a positive number."

**Scenario 6: Attempted Transaction with No Amount Entered**
*   **Given** I am on the "Manage Funds" screen.
*   **When** I leave the "Amount" field empty and click either "Deposit" or "Withdraw".
*   **Then** my "Current Cash Balance" does not change.
*   **And** the "Status" message displays: "❌ Error: Please enter an amount to deposit or withdraw."

---

#### **Non-Functional Requirements (NFRs)**

*   **Performance:** The UI update (balance and status message) must occur within 200ms of the button click.
*   **Data Integrity:** All transactions must be atomic. A failed deposit or withdrawal should not alter the user's balance.
*   **Security:** Server-side validation must be implemented for all inputs to prevent malicious data submission.

#### **Out of Scope**
*   Connecting to real-world payment gateways or banks.
*   Transaction fees or limits.
*   Pending transaction states (all transactions are instant).

---
---

### **User Story: PORT-002**

**ID:** PORT-002
**Title:** Execute Trades (Buy & Sell Shares)
**User Story:** As a `platform user`, I want to `buy and sell shares of available stocks` so that `I can build and manage my investment portfolio`.
**Business Value:** Core platform functionality. Enables the primary user activity of simulated trading, which is central to the product's purpose.
**Priority:** High

---

#### **UI/UX Specifications**

**Framework:** Gradio

**Wireframe/Layout:** The functionality will be hosted within a dedicated tab named "Execute Trade".

```
+-------------------------------------------------------------------+
| [Portfolio Dashboard] [Execute Trade] [Manage Funds] [History]    |  <-- gr.Tabs
+-------------------------------------------------------------------+
|                                                                   |
|   Execute a Trade                                                 |  <-- gr.Markdown
|   ---------------                                                 |
|                                                                   |
|   Cash Available: [ $8,000.00 ]                                   |  <-- gr.Number (label="Cash Available", interactive=False)
|                                                                   |
|   Stock Symbol:   [ AAPL        ]  Current Price: [ $150.25 ]      |  <-- gr.Textbox, gr.Number (interactive=False)
|   Quantity:       [ 10          ]  Estimated Cost:[ $1,502.50 ]    |  <-- gr.Number, gr.Number (interactive=False)
|                                                                   |
|   [     Buy     ]  [    Sell     ]                                |  <-- gr.Button, gr.Button
|                                                                   |
|   +-------------------------------------------------------------+ |
|   | Status: ✅ Success: Purchased 10 shares of AAPL at $150.25.  | |  <-- gr.Markdown (label="Status")
|   +-------------------------------------------------------------+ |
|                                                                   |
+-------------------------------------------------------------------+
```
*Note: The "Current Price" and "Estimated Cost" fields should update automatically when the user types in the "Stock Symbol" and "Quantity" fields.*

**Component Specifications:**
*   `gr.Tab(label="Execute Trade")`: Contains all components for this story.
*   `gr.Number(label="Cash Available", interactive=False)`: Displays the user's current cash balance.
*   `gr.Textbox(label="Stock Symbol")`: Input for the stock symbol (e.g., 'AAPL'). Should trigger a price lookup on change.
*   `gr.Number(label="Current Price", interactive=False)`: Displays the price returned from `get_share_price(symbol)`.
*   `gr.Number(label="Quantity", minimum=1, precision=0)`: Integer input for the number of shares.
*   `gr.Number(label="Estimated Cost", interactive=False)`: Displays `Current Price * Quantity`.
*   `gr.Button("Buy")`: A button to trigger the buy action.
*   `gr.Button("Sell")`: A button to trigger the sell action.
*   `gr.Markdown(label="Status")`: A component to display all success and error messages.

---

#### **Success and Error Messages**

**Success Messages:**
1.  **Buy:** "✅ Success: Purchased {quantity} shares of {symbol} at ${price_per_share}. Total cost: ${total_cost}."
2.  **Sell:** "✅ Success: Sold {quantity} shares of {symbol} at ${price_per_share}. Total credit: ${total_credit}."

**Error Messages:**
1.  **Insufficient Funds:** "❌ Error: Insufficient funds to buy {quantity} shares of {symbol}. Cost is ${total_cost}, but you only have ${cash_balance}."
2.  **Insufficient Shares to Sell:** "❌ Error: Cannot sell {quantity} shares of {symbol}. You only own {shares_owned}."
3.  **Invalid Symbol:** "❌ Error: Stock symbol '{symbol}' is not valid or has no price available."
4.  **Invalid Quantity:** "❌ Error: Quantity must be a positive whole number."
5.  **Backend/API Failure:** "❌ Error: The trade could not be completed due to a system error. Please try again later."

---

#### **Acceptance Criteria (Gherkin Format)**

**Scenario 1: Successful Buy Order**
*   **Given** I am on the "Execute Trade" screen with a "Cash Available" of `$10,000.00`.
*   **And** the price of 'AAPL' is `$150.00`.
*   **When** I enter `AAPL` in "Stock Symbol" and `10` in "Quantity".
*   **Then** the "Estimated Cost" displays `$1,500.00`.
*   **When** I click the "Buy" button.
*   **Then** my "Cash Available" updates to `$8,500.00`.
*   **And** the "Status" message displays: "✅ Success: Purchased 10 shares of AAPL at $150.00. Total cost: $1,500.00."
*   **And** my portfolio now holds 10 shares of 'AAPL'.

**Scenario 2: Successful Sell Order**
*   **Given** I am on the "Execute Trade" screen with a "Cash Available" of `$5,000.00` and I own `20` shares of 'TSLA'.
*   **And** the price of 'TSLA' is `$200.00`.
*   **When** I enter `TSLA` in "Stock Symbol", `5` in "Quantity", and click the "Sell" button.
*   **Then** my "Cash Available" updates to `$6,000.00`.
*   **And** the "Status" message displays: "✅ Success: Sold 5 shares of TSLA at $200.00. Total credit: $1,000.00."
*   **And** my portfolio now holds 15 shares of 'TSLA'.

**Scenario 3: Attempted Buy Order with Insufficient Funds**
*   **Given** I am on the "Execute Trade" screen with a "Cash Available" of `$1,000.00`.
*   **And** the price of 'GOOGL' is `$130.00`.
*   **When** I enter `GOOGL` in "Stock Symbol", `10` in "Quantity" (Estimated Cost: $1,300.00), and click "Buy".
*   **Then** my "Cash Available" remains `$1,000.00`.
*   **And** my portfolio holdings do not change.
*   **And** the "Status" message displays: "❌ Error: Insufficient funds to buy 10 shares of GOOGL. Cost is $1,300.00, but you only have $1,000.00."

**Scenario 4: Attempted Sell Order for Unowned Shares**
*   **Given** I am on the "Execute Trade" screen and I own `5` shares of 'AAPL'.
*   **When** I enter `AAPL` in "Stock Symbol", `10` in "Quantity", and click "Sell".
*   **Then** my "Cash Available" and portfolio holdings do not change.
*   **And** the "Status" message displays: "❌ Error: Cannot sell 10 shares of AAPL. You only own 5."

**Scenario 5: Attempted Trade with an Invalid Symbol**
*   **Given** I am on the "Execute Trade" screen.
*   **When** I enter `INVALID` in "Stock Symbol".
*   **Then** the "Current Price" field shows an error or is blank.
*   **And** if I enter a quantity and click "Buy" or "Sell", the "Status" message displays: "❌ Error: Stock symbol 'INVALID' is not valid or has no price available."

---

#### **Non-Functional Requirements (NFRs)**

*   **Performance:** The `get_share_price()` call and subsequent UI update for "Current Price" and "Estimated Cost" must complete within 500ms of user input.
*   **Dependencies:** This story is dependent on the `get_share_price(symbol)` function being available and responsive.

#### **Out of Scope**
*   Different order types (e.g., limit, stop-loss). All trades are market orders.
*   Real-time, streaming price updates. Prices are fetched on-demand.
*   Trading fees or commissions.

---
---

*Note: The remaining stories (PORT-003: View Portfolio Dashboard, PORT-004: View Transaction History) would follow the exact same detailed format, specifying their unique UI components (`gr.Dataframe`), success/error states (e.g., handling an API failure when fetching prices for the dashboard), and comprehensive acceptance criteria.*