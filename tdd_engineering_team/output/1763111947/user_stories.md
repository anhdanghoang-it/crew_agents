### **Epic: Account Management & Trading Simulation**

This epic covers the core functionalities for users to manage their trading simulation account, including cash management, trading operations, and portfolio reporting.

---

### **User Story: US-001 - User Account Creation**

*   **ID:** US-001
*   **Title:** User Creates a New Trading Simulation Account
*   **User Story:** As a new user, I want to create an account with an initial deposit, so that I can start using the trading simulation platform.
*   **Business Value:** This is the primary entry point for new users. A seamless account creation process is critical for user acquisition and platform adoption.
*   **Priority:** Critical

#### **Acceptance Criteria (AC)**

*   **AC-1: Successful Account Creation (Happy Path)**
    *   **Given** I am a new user on the account creation screen.
    *   **When** I enter a unique username, a password, and an initial deposit amount of $10,000.
    *   **Then** the system creates a new user account for me.
    *   **And** my initial cash balance is set to $10,000.
    *   **And** the system displays a success message: "Success: Account 'username' created with an initial deposit of $10,000.00."
    *   **And** a 'Deposit' transaction for $10,000 is recorded in my transaction history.

*   **AC-2: Attempt to Create an Account with a Non-Unique Username**
    *   **Given** a user with the username 'trader123' already exists.
    *   **When** I attempt to create a new account with the username 'trader123'.
    *   **Then** the system rejects the account creation.
    *   **And** the system displays an error message: "Error: Username 'trader123' is already taken. Please choose a different username."

*   **AC-3: Attempt to Create an Account with Invalid Initial Deposit**
    *   **Given** I am on the account creation screen.
    *   **When** I enter a non-numeric value like "abc" or a negative value like "-100" for the initial deposit.
    *   **Then** the system rejects the account creation.
    *   **And** the system displays an error message: "Error: Initial deposit must be a positive number."

#### **UI/UX Specifications (Gradio)**

*   **Layout:** A single interface for account creation.
*   **Gradio Components:**
    *   `gr.Textbox(label="Username")`
    *   `gr.Textbox(label="Password", type="password")`
    *   `gr.Number(label="Initial Deposit Amount ($)", value=10000.00, minimum=1.00)`
    *   `gr.Button("Create Account")`
    *   `gr.Textbox(label="Status", interactive=False)`: This component will display all success and error messages.
*   **Wireframe/Mockup:**
    ```
    +-------------------------------------------+
    |         Trading Account Creation          |
    +-------------------------------------------+
    | Username:         [ trader123           ] |
    | Password:         [ ************        ] |
    | Initial Deposit:  [ 10000.00            ] |
    |                   +-------------------+   |
    |                   |  Create Account   |   |
    |                   +-------------------+   |
    | Status:           [ Success: ...        ] |
    +-------------------------------------------+
    ```

#### **Non-Functional Requirements**
*   **Performance:** Account creation and feedback should be completed within 500ms.
*   **Security:** Passwords must be securely hashed and stored. Usernames must be sanitized to prevent injection.

#### **Out of Scope**
*   Email verification, password recovery, "login" functionality (this story is only about creation).

---

### **User Story: US-002 - User Manages Cash Balance (Deposit/Withdraw)**

*   **ID:** US-002
*   **Title:** User Manages Cash Balance by Depositing and Withdrawing Funds
*   **User Story:** As a registered user, I want to deposit and withdraw funds, so that I can manage my cash balance for trading.
*   **Business Value:** Provides users with the flexibility to manage their simulated capital, increasing engagement and realism.
*   **Priority:** High

#### **Acceptance Criteria (AC)**

*   **AC-1: Successful Deposit**
    *   **Given** I am a registered user with a cash balance of $5,000.
    *   **When** I choose to deposit $2,000.
    *   **Then** my new cash balance becomes $7,000.
    *   **And** a success message is displayed: "Success: $2,000.00 deposited. Your new cash balance is $7,000.00."
    *   **And** a 'Deposit' transaction for $2,000 is added to my history.

*   **AC-2: Successful Withdrawal**
    *   **Given** I am a registered user with a cash balance of $7,000.
    *   **When** I choose to withdraw $1,500.
    *   **Then** my new cash balance becomes $5,500.
    *   **And** a success message is displayed: "Success: $1,500.00 withdrawn. Your new cash balance is $5,500.00."
    *   **And** a 'Withdrawal' transaction for $1,500 is added to my history.

*   **AC-3: Attempt to Withdraw More Than Available Balance**
    *   **Given** I am a registered user with a cash balance of $1,000.
    *   **When** I attempt to withdraw $1,500.
    *   **Then** the transaction is rejected.
    *   **And** my cash balance remains $1,000.
    *   **And** an error message is displayed: "Error: Insufficient funds. You cannot withdraw more than your available cash balance of $1,000.00."

*   **AC-4: Attempt to Deposit/Withdraw Invalid Amount**
    *   **Given** I am a registered user.
    *   **When** I attempt to deposit or withdraw a negative amount like "-50" or a zero amount.
    *   **Then** the transaction is rejected.
    *   **And** an error message is displayed: "Error: Amount must be a positive number."

#### **UI/UX Specifications (Gradio)**

*   **Layout:** A tabbed interface. This story focuses on the "Cash Management" tab.
*   **Gradio Components:**
    *   `gr.Number(label="Amount ($)", minimum=0.01)`
    *   `gr.Button("Deposit")`
    *   `gr.Button("Withdraw")`
    *   `gr.Textbox(label="Current Cash Balance", interactive=False)`: To display the user's current cash.
    *   `gr.Textbox(label="Status", interactive=False)`: To display all success and error messages for this flow.
*   **Wireframe/Mockup:**
    ```
    +-------------------------------------------+
    | [Portfolio] [Cash Management] [History]   |
    +-------------------------------------------+
    | Current Cash Balance: [$ 5500.00]          |
    |                                           |
    | Amount ($):       [ 500.00              ] |
    |                   +-----------+ +---------+|
    |                   |  Deposit  | | Withdraw||
    |                   +-----------+ +---------+|
    | Status:           [ Success: ...        ] |
    +-------------------------------------------+
    ```

#### **Non-Functional Requirements**
*   **Performance:** Transaction processing and UI update within 300ms.

#### **Out of Scope**
*   Connection to real payment gateways, transaction fees.

---

### **User Story: US-003 - User Executes Trades (Buy/Sell Shares)**

*   **ID:** US-003
*   **Title:** User Executes Trades by Buying and Selling Shares
*   **User Story:** As a trader, I want to buy and sell shares of specific stocks, so that I can build and manage my investment portfolio.
*   **Business Value:** This is the core functionality of the trading simulation. It directly drives user engagement and platform purpose.
*   **Priority:** Critical

#### **Acceptance Criteria (AC)**

*   **AC-1: Successful Share Purchase (Happy Path)**
    *   **Given** I have a cash balance of $10,000 and 0 shares of 'AAPL'.
    *   **And** the current price of 'AAPL' returned by `get_share_price('AAPL')` is $150.
    *   **When** I enter 'AAPL' as the symbol and '10' as the quantity to buy.
    *   **Then** my cash balance is reduced by $1,500 (10 * $150), becoming $8,500.
    *   **And** my holdings now include 10 shares of 'AAPL'.
    *   **And** a success message is displayed: "Success: Bought 10 shares of AAPL at $150.00 each for a total of $1,500.00."
    *   **And** a 'BUY' transaction is recorded in my history.

*   **AC-2: Successful Share Sale (Happy Path)**
    *   **Given** I have a cash balance of $8,500 and 10 shares of 'AAPL'.
    *   **And** the current price of 'AAPL' is $160.
    *   **When** I enter 'AAPL' as the symbol and '5' as the quantity to sell.
    *   **Then** my cash balance is increased by $800 (5 * $160), becoming $9,300.
    *   **And** my holdings of 'AAPL' are reduced to 5 shares.
    *   **And** a success message is displayed: "Success: Sold 5 shares of AAPL at $160.00 each for a total of $800.00."
    *   **And** a 'SELL' transaction is recorded in my history.

*   **AC-3: Attempt to Buy with Insufficient Funds**
    *   **Given** I have a cash balance of $1,000.
    *   **And** the price of 'TSLA' is $300.
    *   **When** I attempt to buy 4 shares of 'TSLA' (total cost $1,200).
    *   **Then** the transaction is rejected.
    *   **And** my cash balance and holdings remain unchanged.
    *   **And** an error message is displayed: "Error: Insufficient funds. You need $1,200.00 to buy 4 shares of TSLA, but you only have $1,000.00."

*   **AC-4: Attempt to Sell More Shares Than Owned**
    *   **Given** I own 5 shares of 'GOOGL'.
    *   **When** I attempt to sell 10 shares of 'GOOGL'.
    *   **Then** the transaction is rejected.
    *   **And** my holdings remain 5 shares of 'GOOGL'.
    *   **And** an error message is displayed: "Error: Insufficient shares. You cannot sell 10 shares of GOOGL as you only own 5."

*   **AC-5: Attempt to Trade an Invalid Symbol**
    *   **Given** I am on the trading screen.
    *   **When** I attempt to buy a stock with an invalid symbol 'XYZ' for which `get_share_price('XYZ')` fails or returns null.
    *   **Then** the transaction is rejected.
    *   **And** an error message is displayed: "Error: Invalid stock symbol 'XYZ'. Please use a valid symbol (e.g., AAPL, TSLA, GOOGL)."

#### **UI/UX Specifications (Gradio)**

*   **Layout:** A dedicated "Trade" tab.
*   **Gradio Components:**
    *   `gr.Dropdown(label="Action", choices=["BUY", "SELL"])`
    *   `gr.Textbox(label="Stock Symbol (e.g., AAPL, TSLA)")`
    *   `gr.Number(label="Quantity", minimum=1, precision=0)`
    *   `gr.Button("Execute Trade")`
    *   `gr.Textbox(label="Status", interactive=False)`: For all trade-related success/error messages.
*   **Wireframe/Mockup:**
    ```
    +-------------------------------------------+
    | [Portfolio] [Cash Mngmt] [Trade] [History] |
    +-------------------------------------------+
    | Action:           [ BUY v ]               |
    | Stock Symbol:     [ AAPL                ] |
    | Quantity:         [ 10                  ] |
    |                   +-------------------+   |
    |                   |  Execute Trade    |   |
    |                   +-------------------+   |
    | Status:           [ Success: Bought...  ] |
    +-------------------------------------------+
    ```

#### **Out of Scope**
*   Real-time price streams, market/limit orders, trading fees/commissions.

---

### **User Story: US-004 - User Views Portfolio and Transaction History**

*   **ID:** US-004
*   **Title:** User Views Portfolio Summary and Transaction History
*   **User Story:** As a trader, I want to view my current portfolio holdings, their total value, my profit/loss, and a history of all my transactions, so that I can track my performance.
*   **Business Value:** Provides essential feedback and analytics to the user, allowing them to assess their trading strategy and performance, which is key to long-term engagement.
*   **Priority:** High

#### **Acceptance Criteria (AC)**

*   **AC-1: View Portfolio Summary**
    *   **Given** I have a cash balance of $5,000, 10 shares of 'AAPL', and 5 shares of 'TSLA'.
    *   **And** the current price of 'AAPL' is $150 and 'TSLA' is $300.
    *   **And** my total initial deposit was $10,000.
    *   **When** I navigate to the 'Portfolio' view.
    *   **Then** the system displays my current holdings: "AAPL: 10 shares", "TSLA: 5 shares".
    *   **And** it calculates and displays the total value of shares: (10 * $150) + (5 * $300) = $3,000.
    *   **And** it calculates and displays the total portfolio value: $5,000 (cash) + $3,000 (shares) = $8,000.
    *   **And** it calculates and displays the total profit/loss: $8,000 (current value) - $10,000 (initial deposit) = -$2,000.

*   **AC-2: View Transaction History**
    *   **Given** I have made several transactions: a deposit, a purchase of AAPL, and a sale of TSLA.
    *   **When** I navigate to the 'History' view.
    *   **Then** the system displays a list of all transactions in reverse chronological order.
    *   **And** each transaction entry includes the timestamp, type (DEPOSIT, WITHDRAWAL, BUY, SELL), symbol (if applicable), quantity, price per share, and total amount.

*   **AC-3: Empty Portfolio and History View**
    *   **Given** I am a new user who has just created an account and made no trades.
    *   **When** I view my portfolio.
    *   **Then** the share holdings section is empty, and total portfolio value equals my cash balance.
    *   **And** when I view my history, it shows only the initial 'DEPOSIT' transaction.

#### **UI/UX Specifications (Gradio)**

*   **Layout:** Two dedicated tabs: "Portfolio" and "History".
*   **Gradio Components for "Portfolio" Tab:**
    *   `gr.Textbox(label="Total Portfolio Value ($)", interactive=False)`
    *   `gr.Textbox(label="Total Profit / Loss ($)", interactive=False)`
    *   `gr.Textbox(label="Cash Balance ($)", interactive=False)`
    *   `gr.Dataframe(label="Current Holdings", headers=["Symbol", "Quantity", "Current Price", "Total Value"])`
    *   `gr.Button("Refresh")` to update prices and calculations.
*   **Gradio Components for "History" Tab:**
    *   `gr.Dataframe(label="Transaction History", headers=["Timestamp", "Type", "Symbol", "Quantity", "Price", "Total"])`
*   **Wireframe/Mockup ("Portfolio" Tab):**
    ```
    +-------------------------------------------+
    | [Portfolio] [Cash Mngmt] [Trade] [History] |
    +-------------------------------------------+
    | Total Portfolio Value: [$ 8000.00]         |
    | Total Profit / Loss:   [-$ 2000.00]        |
    | Cash Balance:         [$ 5000.00]         |
    | +-----------+                             |
    | | Refresh   |                             |
    | +-----------+                             |
    | Current Holdings:                         |
    | +--------+----------+---------+---------+ |
    | | Symbol | Quantity | Price   | Value   | |
    | +--------+----------+---------+---------+ |
    | | AAPL   | 10       | $150.00 | $1500.00| |
    | | TSLA   | 5        | $300.00 | $1500.00| |
    | +--------+----------+---------+---------+ |
    +-------------------------------------------+
    ```

#### **Non-Functional Requirements**
*   **Performance:** Portfolio calculations and display should update within 1 second of clicking "Refresh".

#### **Out of Scope**
*   Graphical charts, exporting data, advanced filtering/sorting of history.