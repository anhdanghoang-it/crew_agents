# Technical Design Document: Trading Simulation Account Management

## 1. Overview & Architecture

This document outlines the technical design for a simple, single-user trading simulation platform. The architecture follows a clean separation of concerns between a Python backend module responsible for all business logic and a Gradio frontend for user interaction.

*   **Backend (`accounts.py`):** A self-contained Python module providing an `Account` class. This class encapsulates all state (cash, holdings, transactions) and logic (deposits, withdrawals, trades, calculations). It is designed to be completely independent of the UI, returning structured data and handling all business rule validation through custom exceptions.
*   **Frontend (`app.py`):** A Gradio application built using `gr.Blocks` for a custom layout. It serves as a thin presentation layer. It captures user inputs, calls the appropriate backend methods, and displays the structured responses and updated portfolio data. State is managed across user interactions by passing a single `Account` instance through `gr.State`.

This decoupled design allows for independent development and testing of the backend logic and the user interface.



---

## 2. Python Backend Design

### Module Structure

The backend will be contained within a single Python file.

```
trading_app/
├── accounts.py      # Core business logic module
└── app.py           # Gradio frontend application
```

### Class Definitions (`accounts.py`)

The entire backend logic is encapsulated within the `accounts` module.

```python
# accounts.py
from __future__ import annotations
import datetime
from typing import List, Dict, NamedTuple, Literal, Union

# --- Data Models/Schemas ---

TransactionType = Literal["DEPOSIT", "WITHDRAW", "BUY", "SELL"]

class Transaction(NamedTuple):
    """Represents a single financial transaction in the account."""
    timestamp: datetime.datetime
    type: TransactionType
    total_value: float
    symbol: str | None = None
    quantity: int | None = None
    price_per_share: float | None = None

class Holding(NamedTuple):
    """Represents the user's holding of a specific stock."""
    symbol: str
    quantity: int
    current_price: float
    market_value: float

class PortfolioSummary(NamedTuple):
    """Represents a snapshot of the entire portfolio's state."""
    cash_balance: float
    holdings: List[Holding]
    total_portfolio_value: float
    profit_loss: float

# --- Custom Exceptions for Business Logic ---

class InsufficientFundsError(Exception):
    """Raised when an action cannot be completed due to lack of cash."""
    pass

class InsufficientSharesError(Exception):
    """Raised when trying to sell more shares than are owned."""
    pass

class InvalidSymbolError(Exception):
    """Raised when a stock symbol is not found."""
    pass

# --- Share Price Service (Mock) ---

_MOCK_PRICES = {"AAPL": 160.00, "TSLA": 200.00, "GOOGL": 140.00}

def get_share_price(symbol: str) -> float:
    """
    Retrieves the current price for a given stock symbol.
    This is a mock implementation for the simulation.
    
    Args:
        symbol: The stock ticker symbol (e.g., 'AAPL').

    Returns:
        The current price of the share.

    Raises:
        InvalidSymbolError: If the symbol is not in the mock database.
    """
    price = _MOCK_PRICES.get(symbol.upper())
    if price is None:
        raise InvalidSymbolError(f"Invalid stock symbol '{symbol}'. Could not retrieve price.")
    return price

# --- Main Account Class ---

class Account:
    """
    Manages all aspects of a user's trading account, including cash,
    holdings, and transaction history.
    """
    def __init__(self, initial_balance: float = 0.0):
        """Initializes the trading account."""
        self._cash_balance: float = initial_balance
        self._holdings: Dict[str, int] = {}  # e.g., {'AAPL': 100}
        self._transactions: List[Transaction] = []
        if initial_balance > 0:
            self._record_transaction(
                type="DEPOSIT", 
                total_value=initial_balance
            )

    def _record_transaction(self, **kwargs) -> None:
        """A private helper to create and record a new transaction."""
        kwargs['timestamp'] = datetime.datetime.now()
        transaction = Transaction(**kwargs)
        self._transactions.insert(0, transaction) # Insert at beginning for chronological order

    def deposit(self, amount: float) -> None:
        """
        Deposits a specified amount of cash into the account.

        Args:
            amount: The amount to deposit. Must be a positive number.

        Raises:
            ValueError: If the amount is not a positive number.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be a positive number.")
        self._cash_balance += amount
        self._record_transaction(type="DEPOSIT", total_value=amount)

    def withdraw(self, amount: float) -> None:
        """
        Withdraws a specified amount of cash from the account.

        Args:
            amount: The amount to withdraw. Must be a positive number.

        Raises:
            ValueError: If the amount is not a positive number.
            InsufficientFundsError: If withdrawal amount exceeds cash balance.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be a positive number.")
        if amount > self._cash_balance:
            raise InsufficientFundsError(
                f"Withdrawal failed. Insufficient funds. You tried to withdraw ${amount:,.2f} "
                f"but only have ${self._cash_balance:,.2f} available."
            )
        self._cash_balance -= amount
        self._record_transaction(type="WITHDRAW", total_value=amount)
    
    def buy_shares(self, symbol: str, quantity: int) -> None:
        """
        Buys a specified quantity of shares for a given stock symbol.

        Args:
            symbol: The stock ticker symbol.
            quantity: The number of shares to buy. Must be a positive integer.

        Raises:
            ValueError: If the quantity is not a positive number.
            InvalidSymbolError: If the stock symbol is not valid.
            InsufficientFundsError: If the cost of the shares exceeds the cash balance.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be a positive number.")
        
        price = get_share_price(symbol)
        cost = quantity * price

        if cost > self._cash_balance:
            raise InsufficientFundsError(
                f"Purchase failed. Insufficient funds. "
                f"Cost is ${cost:,.2f} but you only have ${self._cash_balance:,.2f}."
            )

        self._cash_balance -= cost
        self._holdings[symbol] = self._holdings.get(symbol, 0) + quantity
        self._record_transaction(
            type="BUY",
            symbol=symbol,
            quantity=quantity,
            price_per_share=price,
            total_value=cost,
        )

    def sell_shares(self, symbol: str, quantity: int) -> None:
        """
        Sells a specified quantity of owned shares for a given stock symbol.

        Args:
            symbol: The stock ticker symbol.
            quantity: The number of shares to sell. Must be a positive integer.

        Raises:
            ValueError: If the quantity is not a positive number.
            InvalidSymbolError: If the stock symbol is not valid.
            InsufficientSharesError: If trying to sell more shares than owned.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be a positive number.")
        
        owned_quantity = self._holdings.get(symbol, 0)
        if quantity > owned_quantity:
            raise InsufficientSharesError(
                f"Sale failed. You do not own enough shares. You tried to sell "
                f"{quantity} of {symbol} but you only own {owned_quantity}."
            )
        
        price = get_share_price(symbol)
        proceeds = quantity * price

        self._cash_balance += proceeds
        self._holdings[symbol] -= quantity
        if self._holdings[symbol] == 0:
            del self._holdings[symbol] # Clean up empty holdings

        self._record_transaction(
            type="SELL",
            symbol=symbol,
            quantity=quantity,
            price_per_share=price,
            total_value=proceeds,
        )

    def get_portfolio_summary(self) -> PortfolioSummary:
        """
        Calculates and returns a complete summary of the portfolio.

        Returns:
            A PortfolioSummary object with all current financial data.
        """
        holdings_list = []
        holdings_value = 0.0
        for symbol, quantity in self._holdings.items():
            try:
                price = get_share_price(symbol)
                market_value = price * quantity
                holdings_value += market_value
                holdings_list.append(Holding(symbol, quantity, price, market_value))
            except InvalidSymbolError:
                # In a real app, handle this case more gracefully
                # For this simulation, we assume prices are always available for owned stocks
                continue

        total_portfolio_value = self._cash_balance + holdings_value
        
        total_deposited = sum(
            t.total_value for t in self._transactions if t.type == 'DEPOSIT'
        )
        total_withdrawn = sum(
            t.total_value for t in self._transactions if t.type == 'WITHDRAW'
        )
        net_capital_in = total_deposited - total_withdrawn

        profit_loss = total_portfolio_value - net_capital_in

        return PortfolioSummary(
            cash_balance=self._cash_balance,
            holdings=holdings_list,
            total_portfolio_value=total_portfolio_value,
            profit_loss=profit_loss,
        )

    def get_transaction_history(self) -> List[Transaction]:
        """
        Returns the full list of transactions in reverse chronological order.

        Returns:
            A list of all Transaction objects.
        """
        return self._transactions
```

### Backend Response Format

The action methods (`deposit`, `withdraw`, etc.) do not return values directly; they modify the object's state or raise exceptions. The Gradio wrapper functions will call these methods within a `try...except` block and will be responsible for creating a structured response for the UI.

**Success Response (created by Gradio wrapper):**
```json
{
  "success": true,
  "message": "Success: Deposited $500.00. Your new cash balance is $1,500.00."
}
```

**Error Response (created by Gradio wrapper):**
```json
{
  "success": false,
  "message": "Error: Withdrawal failed. Insufficient funds. You tried to withdraw $2,500.00 but only have $2,000.00 available."
}
```

---

## 3. Gradio Frontend Design

### UI Component Mapping

| Backend Method (`Account`) | UI Action | Gradio Input Components | Gradio Button |
| :--- | :--- | :--- | :--- |
| `deposit(amount)` | Deposit Cash | `gr.Number(label="Deposit Amount")` | `gr.Button("Deposit")` |
| `withdraw(amount)` | Withdraw Cash | `gr.Number(label="Withdraw Amount")` | `gr.Button("Withdraw")` |
| `buy_shares(symbol, quantity)` | Buy Shares | `gr.Dropdown(label="Stock Symbol")`<br>`gr.Number(label="Quantity", precision=0)` | `gr.Button("Buy")` |
| `sell_shares(symbol, quantity)`| Sell Shares | `gr.Dropdown(label="Stock Symbol")`<br>`gr.Number(label="Quantity", precision=0)` | `gr.Button("Sell")` |
| `get_portfolio_summary()` | Update Display| *(No direct input)* | *(Triggered by other buttons)* |
| `get_transaction_history()`| Update Display| *(No direct input)* | *(Triggered by other buttons)* |

**Output Components:**
*   `gr.Textbox(label="Status Message")`: Displays success/error messages from all actions.
*   `gr.Textbox(label="Total Portfolio Value")`: Displays `PortfolioSummary.total_portfolio_value`.
*   `gr.Textbox(label="Total Profit / Loss")`: Displays `PortfolioSummary.profit_loss`.
*   `gr.Textbox(label="Cash Balance")`: Displays `PortfolioSummary.cash_balance`.
*   `gr.Dataframe(headers=["Symbol", ...])`: Displays `PortfolioSummary.holdings`.
*   `gr.Dataframe(headers=["Timestamp", ...])`: Displays `get_transaction_history()`.

### User-Facing Messages

All messages are derived directly from the user stories.

| Story ID | Scenario | Message Type | UI Element | Message Text |
| :--- | :--- | :--- | :--- | :--- |
| TRD-001 | Success | Success | Status Message | `Success: Deposited ${amount:,.2f}. Your new cash balance is ${new_balance:,.2f}.` |
| TRD-001 | Neg/Zero | Error | Status Message | `Error: Deposit amount must be a positive number.` |
| TRD-001 | Non-numeric | Error | Status Message | `Error: Please enter a valid numerical amount for the deposit.` (Handled by `gr.Number`) |
| TRD-002 | Success | Success | Status Message | `Success: Withdrew ${amount:,.2f}. Your new cash balance is ${new_balance:,.2f}.` |
| TRD-002 | Insufficient | Error | Status Message | `Error: Withdrawal failed. Insufficient funds. You tried to withdraw ${amount:,.2f} but only have ${balance:,.2f} available.` |
| TRD-002 | Neg/Zero | Error | Status Message | `Error: Withdrawal amount must be a positive number.` |
| TRD-003 | Success | Success | Status Message | `Success: Bought {quantity} shares of {symbol} at ${price:,.2f} each for a total of ${total:,.2f}. New cash balance: ${new_balance:,.2f}.` |
| TRD-003 | Insufficient | Error | Status Message | `Error: Purchase failed. Insufficient funds. Cost is ${cost:,.2f} but you only have ${balance:,.2f}.` |
| TRD-003 | Invalid Qty | Error | Status Message | `Error: Quantity must be a positive number.` |
| TRD-003 | Invalid Symbol | Error | Status Message | `Error: Invalid stock symbol '{symbol}'. Could not retrieve price.` |
| TRD-004 | Success | Success | Status Message | `Success: Sold {quantity} shares of {symbol} at ${price:,.2f} each for a total of ${total:,.2f}. New cash balance: ${new_balance:,.2f}.` |
| TRD-004 | Insufficient | Error | Status Message | `Error: Sale failed. You do not own enough shares. You tried to sell {quantity} of {symbol} but you only own {owned}.` |
| TRD-004 | Invalid Qty | Error | Status Message | `Error: Quantity must be a positive number.` |
| TRD-005 | No holdings | Info | Holdings Table | A `pandas.DataFrame` that is empty, Gradio will display "No data". |

### UI Layout & Workflow

The UI will be constructed using `gr.Blocks` to achieve a two-column layout.

```
+---------------------------------------------------------------------------------------+
|                                  Trading Simulation                                   |
+---------------------------------------------------------------------------------------+
| gr.Column (Actions)                             | gr.Column (Portfolio Display)         |
| +-------------------------------------------+   | +-----------------------------------+ |
| | gr.Textbox (Status Message)               |   | | gr.Tabs                           | |
| |                                           |   | | +-------------------------------+ | |
| +-------------------------------------------+   | | | Tab: Portfolio Summary          | | |
| | gr.Group (Cash Management)                |   | | | gr.Textbox(Total Value)         | | |
| |   gr.Number(Deposit Amount)               |   | | | gr.Textbox(Profit/Loss)         | | |
| |   gr.Button(Deposit)                      |   | | | gr.Textbox(Cash Balance)        | | |
| |   ---                                     |   | | | gr.Dataframe(Holdings)          | | |
| |   gr.Number(Withdraw Amount)              |   | | +-------------------------------+ | |
| |   gr.Button(Withdraw)                     |   | | | Tab: Transaction History        | | |
| +-------------------------------------------+   | | | gr.Dataframe(Transactions)      | | |
| | gr.Group (Trading Actions)                |   | | +-------------------------------+ | |
| |   gr.Dropdown(Stock Symbol)               |   | +-----------------------------------+ |
| |   gr.Number(Quantity, precision=0)        |   |                                     | |
| |   gr.Row                                  |   |                                     | |
| |     gr.Button(Buy)   gr.Button(Sell)      |   |                                     | |
| +-------------------------------------------+   |                                     | |
+-------------------------------------------------+-------------------------------------+
```

**Workflow:**
1.  User interacts with an input component (e.g., types "500" into "Deposit Amount").
2.  User clicks an action button (e.g., "Deposit").
3.  The button's `.click()` event triggers a Python wrapper function.
4.  The wrapper function reads the inputs and the current `Account` object from `gr.State`.
5.  It calls the corresponding method on the `Account` object (e.g., `account.deposit(500)`).
6.  The backend method either succeeds (modifying state) or raises an exception.
7.  The wrapper function catches any exception, formats the appropriate success/error message.
8.  The wrapper function calls `account.get_portfolio_summary()` and `account.get_transaction_history()` to get the latest data.
9.  The wrapper function returns a tuple containing the updated values for all output components (`Status Message`, `Cash Balance`, `Holdings Table`, etc.).
10. Gradio automatically updates the UI with the returned values.

### Input Validation & Error Display

*   **Client-Side (Gradio):** Basic type validation is handled by Gradio components. `gr.Number` prevents non-numeric text entry. `precision=0` ensures integer input for quantity.
*   **Server-Side (Backend):** All business logic validation (e.g., positive amounts, sufficient funds/shares) is performed in the `Account` class methods.
*   **Error Display:** When a backend method raises an exception, the Gradio wrapper function catches it, formats the exception message into a user-friendly error string (as defined in the table above), and displays it in the shared `gr.Textbox(label="Status Message")`. The other UI elements are not updated, preserving the state before the failed transaction.

---

## 4. Integration Points

### Backend-Frontend Communication

Communication is achieved through direct Python function calls. The Gradio application will hold an instance of the `Account` class in `gr.State`. Event handlers (wrapper functions) receive this state object, call its public methods, and return data formatted for Gradio components.

```python
# Pseudo-code for a Gradio event handler
def handle_deposit(account_state, deposit_amount):
    try:
        # 1. Call backend method
        account_state.deposit(deposit_amount)
        
        # 2. Format success response
        summary = account_state.get_portfolio_summary()
        message = f"Success: Deposited ${deposit_amount:,.2f}. Your new cash balance is ${summary.cash_balance:,.2f}."
        
        # 3. Get all updated data
        history = account_state.get_transaction_history()
        
        # 4. Return updates for all UI components
        return {
            status_box: message,
            cash_balance_box: f"${summary.cash_balance:,.2f}",
            portfolio_value_box: f"${summary.total_portfolio_value:,.2f}",
            # ... other components ...
            transaction_history_df: format_history_for_gradio(history)
        }
        
    except (ValueError, InsufficientFundsError) as e:
        # 5. Handle error, return only the error message
        return {
            status_box: f"Error: {e}"
        }
```

### Data Flow Diagram

`User Input` -> `Gradio Components` -> `Gradio Event Handler` -> `Account Method Call` -> `State Change / Exception` -> `Handler formats Response` -> `Handler gets updated summary` -> `Return values` -> `Gradio Components Update`

---

## 5. Implementation Examples

### Backend Usage Example

```python
from accounts import Account, InsufficientFundsError

# Create an account
my_account = Account()

# Deposit funds
try:
    my_account.deposit(10000)
    print("Deposit successful.")
except ValueError as e:
    print(e)

# Buy shares
try:
    my_account.buy_shares("AAPL", 10)
    print("Purchase successful.")
except (ValueError, InsufficientFundsError, InvalidSymbolError) as e:
    print(e)

# Get summary
summary = my_account.get_portfolio_summary()
print(f"Cash Balance: {summary.cash_balance}")
print(f"Total Value: {summary.total_portfolio_value}")
```

### Frontend Integration Example (`app.py`)

```python
import gradio as gr
import pandas as pd
from accounts import Account, InsufficientFundsError, InsufficientSharesError, InvalidSymbolError

# --- UI Helper Functions ---
def format_portfolio_summary(summary):
    """Formats the summary object into strings and a DataFrame for Gradio."""
    cash_str = f"${summary.cash_balance:,.2f}"
    value_str = f"${summary.total_portfolio_value:,.2f}"
    pl_prefix = "+" if summary.profit_loss >= 0 else ""
    pl_str = f"{pl_prefix}${summary.profit_loss:,.2f}"
    
    holdings_df = pd.DataFrame(summary.holdings)
    if not holdings_df.empty:
        holdings_df['current_price'] = holdings_df['current_price'].apply(lambda x: f"${x:,.2f}")
        holdings_df['market_value'] = holdings_df['market_value'].apply(lambda x: f"${x:,.2f}")
    return cash_str, value_str, pl_str, holdings_df

def format_transaction_history(history):
    """Formats the transaction list into a DataFrame for Gradio."""
    if not history:
        return pd.DataFrame()
    history_df = pd.DataFrame(history)
    # Format for display
    history_df['timestamp'] = history_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    history_df['total_value'] = history_df['total_value'].apply(lambda x: f"${x:,.2f}")
    history_df = history_df.fillna("-") # Replace NaN with dash for cleaner look
    return history_df

# --- Gradio Event Handlers ---
def update_all_outputs(account: Account):
    """Helper to refresh all display components from the account state."""
    summary = account.get_portfolio_summary()
    history = account.get_transaction_history()
    
    cash, value, pl, holdings_df = format_portfolio_summary(summary)
    history_df = format_transaction_history(history)
    
    return {
        cash_balance_box: cash,
        portfolio_value_box: value,
        profit_loss_box: pl,
        holdings_df: holdings_df,
        transaction_history_df: history_df
    }

def handle_deposit(account: Account, amount: float):
    if not amount:
        return {status_box: "Error: Please enter a deposit amount."}
    try:
        account.deposit(amount)
        summary = account.get_portfolio_summary()
        msg = f"Success: Deposited ${amount:,.2f}. Your new cash balance is ${summary.cash_balance:,.2f}."
        
        updates = update_all_outputs(account)
        updates[status_box] = msg
        return updates
    except ValueError as e:
        return {status_box: f"Error: {e}"}

# ... other handlers for withdraw, buy, sell ...

# --- Build the Gradio App ---
with gr.Blocks(title="Trading Simulation") as demo:
    account_state = gr.State(Account) # Initialize the backend Account object

    gr.Markdown("# Trading Simulation")
    
    with gr.Row():
        with gr.Column(scale=1):
            # ... Define all the input components ...
            status_box = gr.Textbox(label="Status Message", interactive=False)
            
            with gr.Group():
                deposit_amount = gr.Number(label="Deposit Amount")
                deposit_btn = gr.Button("Deposit")
            # ... and so on for withdraw, buy, sell ...

        with gr.Column(scale=2):
            # ... Define all the output components ...
            with gr.Tabs():
                with gr.TabItem("Portfolio Summary"):
                    portfolio_value_box = gr.Textbox(label="Total Portfolio Value", interactive=False)
                    profit_loss_box = gr.Textbox(label="Total Profit / Loss", interactive=False)
                    cash_balance_box = gr.Textbox(label="Cash Balance", interactive=False)
                    holdings_df = gr.Dataframe(headers=["symbol", "quantity", "current_price", "market_value"])
                with gr.TabItem("Transaction History"):
                    transaction_history_df = gr.Dataframe()

    # Define component list for outputs
    all_outputs = [status_box, cash_balance_box, portfolio_value_box, profit_loss_box, holdings_df, transaction_history_df]

    # Wire up events
    deposit_btn.click(
        fn=handle_deposit, 
        inputs=[account_state, deposit_amount],
        # outputs=all_outputs # This will cause an error due to dictionary return, Gradio handles dict returns automatically
    )
    # ... wire up other buttons ...
    
# demo.launch() # To run the app
```

---

## 6. Testing & QA Guidelines

QA can validate the application by following the acceptance criteria in the user stories.

**General Test Setup:**
1.  Launch the Gradio application (`python app.py`).
2.  The application should start with a $0 balance and no holdings or transactions.

**Test Cases (Example):**

*   **TRD-001: Deposit Cash**
    *   **TC1.1 (Success):** Enter `500` in "Deposit Amount", click "Deposit".
        *   **Verify:** Status message is "Success: Deposited $500.00. Your new cash balance is $500.00.".
        *   **Verify:** "Cash Balance" box shows "$500.00".
        *   **Verify:** A "DEPOSIT" transaction for $500.00 appears in the "Transaction History" tab.
    *   **TC1.2 (Error):** Enter `-100` in "Deposit Amount", click "Deposit".
        *   **Verify:** Status message is "Error: Deposit amount must be a positive number.".
        *   **Verify:** Cash balance and transaction history do not change.

*   **TRD-004: Sell Shares**
    *   **Setup:** First, deposit $10,000 and buy 20 shares of TSLA.
    *   **TC4.1 (Success):** Select "TSLA", enter `10` in "Quantity", click "Sell".
        *   **Verify:** Status message is "Success: Sold 10 shares of TSLA at $200.00 each for a total of $2,000.00. New cash balance: ...".
        *   **Verify:** "Holdings" table updates to show 10 shares of TSLA.
        *   **Verify:** Cash balance increases by $2,000.
        *   **Verify:** A "SELL" transaction is added to history.
    *   **TC4.2 (Insufficient Shares):** Select "TSLA", enter `25` in "Quantity", click "Sell".
        *   **Verify:** Status message is "Error: Sale failed. You do not own enough shares. You tried to sell 25 of TSLA but you only own 20.".
        *   **Verify:** Cash balance, holdings, and transaction history do not change from the setup state.

*   **TRD-005: Portfolio Summary**
    *   **TC5.1 (Live Update):** After every successful transaction (deposit, withdraw, buy, sell), verify that all fields in the "Portfolio Summary" tab (`Total Portfolio Value`, `Total Profit / Loss`, `Cash Balance`, `Holdings` table) are updated immediately and accurately reflect the new state of the account. The calculations should match those in the user story's acceptance criteria.