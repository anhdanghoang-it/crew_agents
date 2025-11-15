# Technical Design Document: Trading Simulation Platform

## 1. Overview & Architecture

This document outlines the technical design for a simple, single-user trading simulation platform. The application is architected as a two-layer system:

*   **Python Backend:** A self-contained, stateless Python module (`accounts`) provides the core business logic. The central class, `Account`, encapsulates all data and operations like deposits, withdrawals, trades, and reporting. The backend is designed to be completely independent of the user interface.
*   **Gradio Frontend:** A web-based user interface built with Gradio provides a simple, interactive prototype for users. It communicates directly with the Python backend to perform actions and display data.

The architecture is designed for simplicity, with the Gradio application holding the state of the single `Account` object in memory using `gr.State`. All business rules, calculations, and error handling are managed by the backend, ensuring a clean separation of concerns. The frontend is responsible only for presenting data and capturing user input.



---

## 2. Python Backend Design

### Module Structure

The backend will be contained within a single Python module named `accounts`.

```
trading_simulator/
├── accounts/
│   ├── __init__.py
│   ├── account.py      # Contains Account class, data models, and exceptions
│   └── price_api.py    # Contains get_share_price() function
└── app.py              # The main Gradio application file
```

### Data Models/Schemas

We will use `dataclasses` for clear, type-hinted data structures and an `Enum` for transaction types.

```python
# In accounts/account.py

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List

class TransactionType(Enum):
    """Enumeration for transaction types."""
    INIT = auto()
    DEPOSIT = auto()
    WITHDRAW = auto()
    BUY = auto()
    SELL = auto()

@dataclass
class Transaction:
    """Represents a single financial transaction."""
    timestamp: datetime
    type: TransactionType
    symbol: str | None
    quantity: int | None
    unit_price: float | None
    total: float

@dataclass
class PortfolioSummary:
    """A snapshot of the account's financial status."""
    cash_balance: float
    holdings_value: float
    total_portfolio_value: float
    profit_loss: float
    holdings: Dict[str, int] # e.g., {'AAPL': 50, 'TSLA': 10}
    total_deposits: float
```

### Error Handling Strategy

Custom exceptions will be defined to provide specific error details from the backend to the frontend. All custom exceptions will inherit from a base `AccountError`.

```python
# In accounts/account.py

class AccountError(Exception):
    """Base exception for all account-related errors."""
    pass

class InsufficientFundsError(AccountError):
    """Raised when an operation cannot be completed due to lack of cash."""
    pass

class InsufficientSharesError(AccountError):
    """Raised when trying to sell more shares than owned."""
    pass

class InvalidOperationError(AccountError):
    """Raised for invalid inputs, like non-positive amounts."""
    pass
```

### Backend Response Format

While the backend methods will primarily raise exceptions on failure, the controller functions that bridge the backend and frontend will catch these exceptions and return structured dictionaries. This design is robust for potential future API expansion.

*   **Success Response:**
    ```json
    {
        "status": "success",
        "message": "User-facing success message.",
        "data": { ... }
    }
    ```
*   **Error Response:**
    ```json
    {
        "status": "error",
        "message": "User-facing error message."
    }
    ```

### Class Definitions

#### `accounts.price_api.py`

This module provides the external dependency for fetching share prices.

```python
def get_share_price(symbol: str) -> float:
    """
    Retrieves the current market price for a given stock symbol.
    Includes a test implementation for known symbols.

    Args:
        symbol: The stock symbol (e.g., 'AAPL').

    Returns:
        The current price per share.

    Raises:
        ValueError: If the symbol is not found in the test data.
    """
    # Test implementation with fixed prices
    prices = {
        "AAPL": 150.00,
        "TSLA": 200.00,
        "GOOGL": 130.00,
    }
    price = prices.get(symbol.upper())
    if price is None:
        raise ValueError(f"Could not retrieve price for symbol: {symbol}")
    return price
```

#### `accounts.account.py`

This is the core class containing all business logic.

```python
from .price_api import get_share_price
# ... other imports: datetime, Enum, dataclasses, typing ...

class Account:
    """
    Manages a user's trading account, including cash balance,
    holdings, and transaction history.
    """

    def __init__(self, initial_deposit: float):
        """
        Initializes a new trading account.

        Args:
            initial_deposit: The starting cash balance.

        Raises:
            InvalidOperationError: If the initial deposit is not a positive number.
        """
        if initial_deposit <= 0:
            raise InvalidOperationError("Initial deposit must be a positive number.")

        self._cash_balance: float = initial_deposit
        self._total_deposits: float = initial_deposit
        self._holdings: Dict[str, int] = {}  # symbol -> quantity
        self._transactions: List[Transaction] = []
        
        self._log_transaction(
            type=TransactionType.INIT,
            total=initial_deposit
        )

    @property
    def cash_balance(self) -> float:
        """Returns the current cash balance."""
        return self._cash_balance

    def _log_transaction(self, type: TransactionType, total: float, symbol: str | None = None, quantity: int | None = None, unit_price: float | None = None):
        """A private helper to record a transaction."""
        # Implementation details omitted for brevity...
        pass
    
    def deposit(self, amount: float) -> None:
        """
        Adds funds to the account's cash balance.

        Args:
            amount: The amount to deposit.

        Raises:
            InvalidOperationError: If the amount is not a positive number.
        """
        if amount <= 0:
            raise InvalidOperationError("Amount must be a positive number.")
        self._cash_balance += amount
        self._total_deposits += amount
        self._log_transaction(type=TransactionType.DEPOSIT, total=amount)

    def withdraw(self, amount: float) -> None:
        """
        Removes funds from the account's cash balance.

        Args:
            amount: The amount to withdraw.

        Raises:
            InvalidOperationError: If the amount is not a positive number.
            InsufficientFundsError: If the withdrawal amount exceeds the cash balance.
        """
        if amount <= 0:
            raise InvalidOperationError("Amount must be a positive number.")
        if amount > self._cash_balance:
            raise InsufficientFundsError(f"Withdrawal failed. Insufficient funds. Available: ${self._cash_balance:,.2f}.")
        self._cash_balance -= amount
        self._total_deposits -= amount # Tracks net deposits for P/L
        self._log_transaction(type=TransactionType.WITHDRAW, total=-amount)
    
    def buy_shares(self, symbol: str, quantity: int) -> float:
        """
        Purchases shares of a stock.

        Args:
            symbol: The stock symbol to buy.
            quantity: The number of shares to buy.

        Returns:
            The total cost of the transaction.

        Raises:
            InvalidOperationError: If quantity is not a positive integer.
            InsufficientFundsError: If the total cost exceeds the cash balance.
            ValueError: If the share price cannot be retrieved.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise InvalidOperationError("Quantity must be a positive whole number.")
        
        price = get_share_price(symbol)
        total_cost = price * quantity

        if total_cost > self._cash_balance:
            raise InsufficientFundsError(f"Purchase failed. Insufficient funds. Required: ${total_cost:,.2f}, Available: ${self._cash_balance:,.2f}.")
        
        self._cash_balance -= total_cost
        self._holdings[symbol] = self._holdings.get(symbol, 0) + quantity
        self._log_transaction(
            type=TransactionType.BUY,
            symbol=symbol,
            quantity=quantity,
            unit_price=price,
            total=-total_cost
        )
        return total_cost

    def sell_shares(self, symbol: str, quantity: int) -> float:
        """
        Sells shares of a stock.

        Args:
            symbol: The stock symbol to sell.
            quantity: The number of shares to sell.

        Returns:
            The total value of the shares sold.

        Raises:
            InvalidOperationError: If quantity is not a positive integer.
            InsufficientSharesError: If trying to sell more shares than owned.
            ValueError: If the share price cannot be retrieved.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise InvalidOperationError("Quantity must be a positive whole number.")

        owned_quantity = self._holdings.get(symbol, 0)
        if owned_quantity == 0:
            raise InsufficientSharesError(f"Sale failed. You do not own any shares of {symbol}.")
        if quantity > owned_quantity:
            raise InsufficientSharesError(f"Sale failed. Cannot sell {quantity} shares of {symbol}, you only own {owned_quantity}.")

        price = get_share_price(symbol)
        total_value = price * quantity

        self._cash_balance += total_value
        self._holdings[symbol] -= quantity
        if self._holdings[symbol] == 0:
            del self._holdings[symbol]
        
        self._log_transaction(
            type=TransactionType.SELL,
            symbol=symbol,
            quantity=quantity,
            unit_price=price,
            total=total_value
        )
        return total_value
    
    def get_portfolio_summary(self) -> PortfolioSummary:
        """
        Calculates and returns a summary of the entire portfolio.

        Returns:
            A PortfolioSummary object with the account's current status.
        """
        holdings_value = 0.0
        for symbol, quantity in self._holdings.items():
            try:
                holdings_value += get_share_price(symbol) * quantity
            except ValueError:
                # If a price can't be fetched, that holding's value is 0 for this summary
                pass
        
        total_portfolio_value = self._cash_balance + holdings_value
        profit_loss = total_portfolio_value - self._total_deposits
        
        return PortfolioSummary(
            cash_balance=self._cash_balance,
            holdings_value=holdings_value,
            total_portfolio_value=total_portfolio_value,
            profit_loss=profit_loss,
            holdings=self._holdings,
            total_deposits=self._total_deposits
        )

    def get_transaction_history(self) -> List[Transaction]:
        """
        Returns a list of all transactions, most recent first.

        Returns:
            A list of Transaction objects.
        """
        return sorted(self._transactions, key=lambda t: t.timestamp, reverse=True)
```

---

## 3. Gradio Frontend Design

### UI Component Mapping

| Backend Method                 | UI Action                     | Gradio Components                                                                                                          | Tab                 |
| ------------------------------ | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| `Account(initial_deposit)`     | Create Account                | `gr.Number(label="Initial Deposit Amount ($)")`, `gr.Button("Create Account")`                                             | Initial View        |
| `account.deposit(amount)`      | Deposit Funds                 | `gr.Number(label="Amount ($)")`, `gr.Button("Deposit")`                                                                    | Account Actions     |
| `account.withdraw(amount)`     | Withdraw Funds                | `gr.Number(label="Amount ($)")`, `gr.Button("Withdraw")`                                                                   | Account Actions     |
| `account.buy_shares(s, q)`     | Buy Shares                    | `gr.Dropdown(label="Stock Symbol")`, `gr.Number(label="Quantity")`, `gr.Button("Buy")`                                     | Trade               |
| `account.sell_shares(s, q)`    | Sell Shares                   | `gr.Dropdown(label="Stock Symbol")`, `gr.Number(label="Quantity")`, `gr.Button("Sell")`                                     | Trade               |
| `account.get_portfolio_summary()` | Update Summary Panel        | `gr.Markdown()` (triggered after every successful state change)                                                            | Always Visible      |
| `account.get_transaction_history()` | View Transaction History    | `gr.DataFrame()` (triggered after every successful state change or tab selection)                                        | Transaction History |

### User-Facing Messages

A central `gr.Textbox(label="System Status")` will display these messages.

| Story ID | Trigger                                 | Message Type | Message Text                                                                                    |
| -------- | --------------------------------------- | ------------ | ----------------------------------------------------------------------------------------------- |
| ACC-001  | Successful Account Creation             | Success      | "Account created successfully with an initial deposit of $[amount]."                            |
| ACC-001  | Invalid Initial Deposit (<=0)           | Error        | "Initial deposit must be a positive number."                                                    |
| ACC-001  | Invalid Initial Deposit (non-numeric)   | Error        | "Please enter a valid number for the deposit." (Handled by Gradio `Number` component)         |
| ACC-002  | Successful Deposit                      | Success      | "Successfully deposited $[amount]. New cash balance: $[new_balance]."                           |
| ACC-002  | Successful Withdrawal                   | Success      | "Successfully withdrew $[amount]. New cash balance: $[new_balance]."                           |
| ACC-002  | Withdrawal > Balance                    | Error        | "Withdrawal failed. Insufficient funds. Available: $[current_balance]."                        |
| ACC-002  | Deposit/Withdraw amount <= 0            | Error        | "Amount must be a positive number."                                                             |
| TRD-001  | Successful Buy                          | Success      | "Successfully purchased [qty] shares of [symbol] for $[total_cost]."                           |
| TRD-001  | Successful Sell                         | Success      | "Successfully sold [qty] shares of [symbol] for $[total_value]."                                |
| TRD-001  | Buy with Insufficient Funds             | Error        | "Purchase failed. Insufficient funds. Required: $[cost], Available: $[balance]."               |
| TRD-001  | Sell more shares than owned             | Error        | "Sale failed. Cannot sell [qty] shares of [symbol], you only own [owned_qty]."                  |
| TRD-001  | Sell shares not owned                   | Error        | "Sale failed. You do not own any shares of [symbol]."                                           |
| TRD-001  | Trade with quantity <= 0                | Error        | "Quantity must be a positive whole number."                                                     |
| TRD-001  | `get_share_price` fails                 | Error        | "Could not retrieve price for [symbol]. Please try again later."                                |

### UI Layout & Workflow

The UI will have two primary states: "Account Creation" and "Main Application".

**State 1: Account Creation View**
*   **Visibility:** Shown on app launch if no account exists.
*   **Components:**
    *   `gr.Markdown("# Create Your Trading Account")`
    *   `gr.Number(label="Initial Deposit Amount ($)", value=10000)`
    *   `gr.Button("Create Account")`
    *   `gr.Textbox(label="System Status", interactive=False)`
*   **Workflow:** User enters an amount, clicks "Create Account". On success, this view is hidden, and the "Main Application" view becomes visible.

**State 2: Main Application View**
*   **Visibility:** Shown after a successful account creation.
*   **Layout:**
    *   `gr.Blocks()`
        *   `gr.Row()`
            *   `gr.Column(scale=1)`: **Portfolio Summary Panel** (`gr.Markdown`)
            *   `gr.Column(scale=3)`:
                *   `gr.Tabs()`
                    *   `gr.TabItem("Account Actions")`: Deposit/Withdraw controls.
                    *   `gr.TabItem("Trade")`: Buy/Sell controls.
                    *   `gr.TabItem("Transaction History")`: Transaction log `gr.DataFrame`.
                *   `gr.Textbox(label="System Status", interactive=False)`: For all feedback messages.

### Input Validation & Error Display

*   **Client-Side Validation:** `gr.Number` components will be used to prevent non-numeric input. For trading quantity, `precision=0` and `minimum=1` will enforce positive integers.
*   **Server-Side Validation:** The backend is the source of truth. Any invalid operations (e.g., negative amounts, insufficient funds) will be caught by the backend, which raises an exception.
*   **Error Display:** The controller function in `app.py` will catch exceptions from the `Account` methods and format the exception message into the `System Status` textbox. The textbox text will be colored red for errors and green for successes using Gradio's built-in CSS or custom styling.

---

## 4. Integration Points

### Backend-Frontend Communication

Communication is achieved through controller functions defined in `app.py`. These functions serve as the glue between the Gradio UI and the `Account` object.

1.  An `Account` instance is stored in a `gr.State` object, persisting it across UI interactions.
2.  Gradio events (e.g., `buy_button.click()`) trigger a controller function.
3.  The controller function takes input from Gradio components, calls the relevant method on the `Account` object stored in `gr.State`.
4.  It uses a `try...except` block to handle potential `AccountError` exceptions.
5.  It formats a success or error message.
6.  It calls `account.get_portfolio_summary()` and `account.get_transaction_history()` to get the latest state.
7.  It returns all the updated values, which Gradio then uses to update the corresponding output components (`System Status` textbox, `Portfolio Summary` markdown, `Transaction History` dataframe).

### Data Flow Diagram (Buy Shares)

```
User Action:
  [Clicks "Buy" Button in UI]
     |
     v
Gradio Event Handler (`buy_button.click`):
  - Collects `symbol` from Dropdown and `quantity` from Number input.
  - Calls `handle_buy(account_state, symbol, quantity)`
     |
     v
Controller Function (`handle_buy`):
  1. `try:`
  2.   `cost = account.buy_shares(symbol, quantity)`
  3.   `message = "Success: Purchased..."`
  4. `except InsufficientFundsError as e:`
  5.   `message = str(e)`
  6. `summary = account.get_portfolio_summary()`
  7. `history = account.get_transaction_history()`
  8. `return account_state, message, summary, history`
     |
     v
Gradio Updates UI:
  - Updates `gr.State` with the modified `account_state`.
  - Displays `message` in the System Status Textbox.
  - Renders new `summary` in the Portfolio Summary Markdown.
  - Renders new `history` in the Transaction History DataFrame.
```

### Message Mapping

| User Story ID | User-Facing Message Text                                              | UI Element for Display                             |
| ------------- | --------------------------------------------------------------------- | -------------------------------------------------- |
| ACC-001       | "Account created successfully with an initial deposit of $[amount]."   | `gr.Textbox(label="System Status")`                |
| ACC-001       | "Initial deposit must be a positive number."                          | `gr.Textbox(label="System Status")`                |
| ACC-002       | "Successfully deposited $[amount]. New cash balance: $[new_balance]." | `gr.Textbox(label="System Status")`                |
| ACC-002       | "Withdrawal failed. Insufficient funds. Available: $[balance]."      | `gr.Textbox(label="System Status")`                |
| TRD-001       | "Successfully purchased [qty] shares of [symbol] for $[cost]."        | `gr.Textbox(label="System Status")`                |
| TRD-001       | "Purchase failed. Insufficient funds. Required: $[cost], Avail: $[bal]." | `gr.Textbox(label="System Status")`                |
| RPT-001       | Portfolio Summary (e.g., "Cash: $10,000.00")                          | `gr.Markdown()` (Portfolio Summary Panel)          |
| RPT-001       | Transaction History Table                                             | `gr.DataFrame()` (Transaction History Tab)         |

---

## 5. Implementation Examples

### Backend Usage Example (for testing)

```python
# In a test file, e.g., tests/test_account.py
from accounts.account import Account, InsufficientFundsError

# 1. Create an account
try:
    acc = Account(initial_deposit=10000)
    print(f"Account created. Cash: ${acc.cash_balance}")
except Exception as e:
    print(f"Error: {e}")

# 2. Buy shares
try:
    cost = acc.buy_shares("AAPL", 10) # AAPL @ $150
    print(f"Bought AAPL for ${cost:.2f}. New cash: ${acc.cash_balance:.2f}")
except Exception as e:
    print(f"Error: {e}")

# 3. Attempt to buy with insufficient funds
try:
    acc.buy_shares("TSLA", 100) # 100 * $200 = $20,000 required
except InsufficientFundsError as e:
    print(f"Caught expected error: {e}")

# 4. Get summary
summary = acc.get_portfolio_summary()
print(f"Portfolio Value: ${summary.total_portfolio_value:,.2f}")
```

### Frontend Integration Example (`app.py`)

```python
import gradio as gr
from accounts.account import Account, AccountError

# This is a simplified controller function
def handle_deposit(account: Account, amount: float):
    """Controller to handle deposit logic."""
    if account is None:
        return None, "Error: Account not created.", None, None
    
    try:
        account.deposit(amount)
        new_balance = account.cash_balance
        message = f"Successfully deposited ${amount:,.2f}. New cash balance: ${new_balance:,.2f}."
    except AccountError as e:
        message = f"Error: {e}"

    # After any action, fetch the latest state for all UI components
    summary = format_summary_markdown(account.get_portfolio_summary())
    history_df = format_history_dataframe(account.get_transaction_history())
    
    return account, message, summary, history_df

# Gradio UI wiring
with gr.Blocks() as demo:
    # Define gr.State and all UI components
    account_state = gr.State(None) # Initially no account
    status_box = gr.Textbox(label="System Status")
    summary_md = gr.Markdown("### Portfolio Summary")
    history_df = gr.DataFrame(headers=["Timestamp", "Type", ...])
    
    with gr.Tab("Account Actions"):
        deposit_amount = gr.Number(label="Amount ($)")
        deposit_button = gr.Button("Deposit")

    # The .click() event wires the UI to the controller function
    deposit_button.click(
        fn=handle_deposit,
        inputs=[account_state, deposit_amount],
        outputs=[account_state, status_box, summary_md, history_df]
    )

# Note: format_summary_markdown and format_history_dataframe are helper functions
# to convert backend data models into UI-friendly formats (string and pandas DataFrame).
```

---

## 6. Testing & QA Guidelines

### Backend Unit Testing (Pytest)

*   **`Account` Initialization:**
    *   Test that `Account(1000)` succeeds and sets `cash_balance` correctly.
    *   Test that `Account(0)` and `Account(-100)` raise `InvalidOperationError`.
*   **Deposits & Withdrawals:**
    *   Test `deposit(100)` correctly increases `cash_balance`.
    *   Test `deposit(-50)` raises `InvalidOperationError`.
    *   Test `withdraw(100)` correctly decreases `cash_balance`.
    *   Test withdrawing more than `cash_balance` raises `InsufficientFundsError`.
*   **Trading Logic:**
    *   Test successful `buy_shares` reduces cash and increases holdings.
    *   Test `buy_shares` with insufficient funds raises `InsufficientFundsError`.
    *   Test successful `sell_shares` increases cash and decreases holdings.
    *   Test `sell_shares` for a stock not owned raises `InsufficientSharesError`.
    *   Test `sell_shares` for more quantity than owned raises `InsufficientSharesError`.
*   **Reporting:**
    *   After a series of transactions, verify `get_portfolio_summary` calculates all values (cash, holdings value, P&L) correctly.
    *   Verify `get_transaction_history` returns a correctly formatted and ordered list of `Transaction` objects.

### Frontend & E2E QA Validation (Manual Checklist)

QA should execute all scenarios defined in the User Stories' Acceptance Criteria.

*   **ACC-001: Account Creation**
    *   [ ] Verify the initial "Create Account" UI is shown first.
    *   [ ] Enter 10000 and click "Create". Confirm the success message "Account created successfully..." is shown.
    *   [ ] Confirm the main UI appears and the Portfolio Summary shows $10,000 cash.
    *   [ ] Refresh the app, enter -100 and click "Create". Confirm the error message "Initial deposit must be a positive number." is shown.
*   **ACC-002: Fund Management**
    *   [ ] In the "Account Actions" tab, deposit $1000. Verify success message and confirm cash balance in summary updates.
    *   [ ] Withdraw $500. Verify success message and confirm cash balance updates.
    *   [ ] Attempt to withdraw $99,999 (more than balance). Verify the "Insufficient funds" error message is shown and balance is unchanged.
*   **TRD-001: Trading**
    *   [ ] In the "Trade" tab, select "AAPL", enter quantity 10, click "Buy". Verify the success message "Successfully purchased 10 shares...".
    *   [ ] Verify Portfolio Summary updates: cash decreases, holdings value appears, and holdings list shows "AAPL: 10 Shares".
    *   [ ] Select "AAPL", enter quantity 5, click "Sell". Verify success message and check that summary updates correctly (cash increases, holdings show "AAPL: 5 Shares").
    *   [ ] Attempt to sell 100 shares of "AAPL" (more than owned). Verify the "Cannot sell 100 shares..." error.
    *   [ ] Attempt to sell shares of "GOOGL" (not owned). Verify the "You do not own any shares..." error.
*   **RPT-001: Reporting**
    *   [ ] After each action (deposit, buy, sell), confirm the Portfolio Summary panel updates instantly (<1 sec).
    *   [ ] Navigate to the "Transaction History" tab. Verify a new row appears at the top for each transaction with correct details (Type, Symbol, Qty, etc.).