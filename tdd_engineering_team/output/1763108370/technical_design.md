# Technical Design: Account & Portfolio Management System

## 1. Overview & Architecture

This document outlines the technical design for a simple account management and trading simulation system. The system is composed of two primary components: a Python backend module responsible for all business logic and state management, and a Gradio frontend for user interaction.

### 1.1. Architecture

The architecture follows a clean separation of concerns:

*   **Python Backend (`accounts` module):** A self-contained, stateless-logic module centered around the `Account` class. This class encapsulates all rules, calculations, and data for a user's portfolio. It has no knowledge of the user interface and communicates outcomes through return values and custom exceptions. This makes it independently testable and reusable.
*   **Gradio Frontend (`app.py`):** A web-based user interface built with Gradio. It is responsible for rendering UI components, capturing user input, and displaying results. It acts as the controller layer, orchestrating calls to the backend based on user actions.
*   **Integration Layer:** A set of functions within the Gradio application that handle UI events (e.g., button clicks). These functions are responsible for:
    1.  Collecting and validating user input from Gradio components.
    2.  Calling the appropriate methods on a backend `Account` instance.
    3.  Catching exceptions raised by the backend.
    4.  Formatting success or error responses into user-friendly messages.
    5.  Returning the necessary data to update the Gradio UI components.

For this simulation, we will maintain a single, global `Account` instance within the Gradio application's lifecycle to persist the user's state across interactions.

## 2. Python Backend Design

**Module:** `accounts.py`

### 2.1. Module Structure

```
accounts/
├── __init__.py
├── account.py         # Contains the Account class, data models, and exceptions
└── services.py        # Contains external services like get_share_price
```

### 2.2. Data Models/Schemas (`accounts/account.py`)

We will use `dataclasses` for clear, typed data structures.

```python
import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Transaction:
    """Represents a single financial transaction."""
    transaction_type: TransactionType
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    amount: float = 0.0
    symbol: str | None = None
    quantity: int | None = None
    share_price: float | None = None

    def to_dict(self):
        """Converts the transaction to a dictionary for display."""
        return {
            "Time": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Type": self.transaction_type.value,
            "Symbol": self.symbol or "N/A",
            "Quantity": self.quantity or "N/A",
            "Share Price": f"${self.share_price:,.2f}" if self.share_price else "N/A",
            "Amount": f"${self.amount:,.2f}"
        }

@dataclass
class Holding:
    """Represents a user's holding in a single stock."""
    symbol: str
    quantity: int
```

### 2.3. Error Handling Strategy (`accounts/account.py`)

Custom exceptions provide clear error signals from the backend.

```python
class AccountError(Exception):
    """Base exception for all account-related errors."""
    pass

class InvalidAmountError(AccountError):
    """Raised when a transaction amount is invalid (e.g., negative or zero)."""
    pass

class InsufficientFundsError(AccountError):
    """Raised when a withdrawal or purchase exceeds available cash."""
    pass

class InsufficientSharesError(AccountError):
    """Raised when trying to sell more shares than owned."""
    pass

class InvalidSymbolError(AccountError):
    """Raised for an unrecognized or unpriceable stock symbol."""
    pass
```

### 2.4. External Services (`accounts/services.py`)

This module isolates external dependencies, like the price fetching function.

```python
# accounts/services.py
from .account import InvalidSymbolError

def get_share_price(symbol: str) -> float:
    """
    Retrieves the current market price for a given stock symbol.
    Includes a test implementation for known symbols.

    Args:
        symbol: The stock symbol (e.g., 'AAPL').

    Returns:
        The current price as a float.

    Raises:
        InvalidSymbolError: If the symbol is not found.
    """
    # Test implementation
    prices = {"AAPL": 150.25, "TSLA": 200.50, "GOOGL": 130.75}
    price = prices.get(symbol.upper())
    if price is None:
        raise InvalidSymbolError(f"Stock symbol '{symbol}' is not valid or has no price available.")
    return price
```

### 2.5. Class Definition (`accounts/account.py`)

The core business logic is encapsulated within the `Account` class.

```python
# accounts/account.py
# (Imports and data models from above)
from .services import get_share_price

class Account:
    """
    Manages a user's trading account, including cash balance,
    holdings, and transaction history.
    """

    def __init__(self, owner: str, initial_deposit: float = 0.0):
        """
        Initializes a new trading account.

        Args:
            owner: The name of the account owner.
            initial_deposit: The starting cash balance.
        """
        if initial_deposit < 0:
            raise InvalidAmountError("Initial deposit cannot be negative.")

        self.owner: str = owner
        self._cash_balance: float = initial_deposit
        self._holdings: Dict[str, int] = {}  # E.g., {"AAPL": 10}
        self._transactions: List[Transaction] = []
        self._total_deposits: float = 0.0

        if initial_deposit > 0:
            self.deposit(initial_deposit)


    @property
    def cash_balance(self) -> float:
        """Returns the current cash balance."""
        return self._cash_balance

    @property
    def holdings(self) -> Dict[str, int]:
        """Returns a copy of the current stock holdings."""
        return self._holdings.copy()

    def deposit(self, amount: float) -> float:
        """
        Deposits a specified amount into the account.

        Args:
            amount: The positive amount to deposit.

        Returns:
            The new cash balance.

        Raises:
            InvalidAmountError: If the amount is not positive.
        """
        if amount <= 0:
            raise InvalidAmountError("Amount must be a positive number.")

        self._cash_balance += amount
        self._total_deposits += amount
        self._transactions.append(Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=amount
        ))
        return self._cash_balance

    def withdraw(self, amount: float) -> float:
        """
        Withdraws a specified amount from the account.

        Args:
            amount: The positive amount to withdraw.

        Returns:
            The new cash balance.

        Raises:
            InvalidAmountError: If the amount is not positive.
            InsufficientFundsError: If withdrawal amount exceeds cash balance.
        """
        if amount <= 0:
            raise InvalidAmountError("Amount must be a positive number.")
        if amount > self._cash_balance:
            raise InsufficientFundsError(f"Your current balance is ${self._cash_balance:,.2f}.")

        self._cash_balance -= amount
        self._transactions.append(Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=-amount  # Store as negative to represent cash out
        ))
        return self._cash_balance

    def buy_shares(self, symbol: str, quantity: int) -> Dict:
        """
        Executes a buy order for a specified quantity of shares.

        Args:
            symbol: The stock symbol to buy.
            quantity: The number of shares to buy.

        Returns:
            A dictionary containing transaction details for the success message.

        Raises:
            InvalidAmountError: If quantity is not a positive integer.
            InvalidSymbolError: If the symbol is not valid.
            InsufficientFundsError: If the total cost exceeds the cash balance.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise InvalidAmountError("Quantity must be a positive whole number.")
        
        symbol = symbol.upper()
        price_per_share = get_share_price(symbol)
        total_cost = price_per_share * quantity

        if total_cost > self._cash_balance:
            raise InsufficientFundsError(
                f"Cost is ${total_cost:,.2f}, but you only have ${self._cash_balance:,.2f}."
            )

        self._cash_balance -= total_cost
        self._holdings[symbol] = self._holdings.get(symbol, 0) + quantity
        self._transactions.append(Transaction(
            transaction_type=TransactionType.BUY,
            amount=-total_cost,
            symbol=symbol,
            quantity=quantity,
            share_price=price_per_share
        ))
        
        return {
            "symbol": symbol,
            "quantity": quantity,
            "price_per_share": price_per_share,
            "total_cost": total_cost,
        }

    def sell_shares(self, symbol: str, quantity: int) -> Dict:
        """
        Executes a sell order for a specified quantity of shares.

        Args:
            symbol: The stock symbol to sell.
            quantity: The number of shares to sell.

        Returns:
            A dictionary containing transaction details for the success message.

        Raises:
            InvalidAmountError: If quantity is not a positive integer.
            InvalidSymbolError: If the symbol is not valid.
            InsufficientSharesError: If trying to sell more shares than owned.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise InvalidAmountError("Quantity must be a positive whole number.")
        
        symbol = symbol.upper()
        shares_owned = self._holdings.get(symbol, 0)

        if quantity > shares_owned:
            raise InsufficientSharesError(f"You only own {shares_owned}.")

        price_per_share = get_share_price(symbol)
        total_credit = price_per_share * quantity

        self._cash_balance += total_credit
        self._holdings[symbol] -= quantity
        if self._holdings[symbol] == 0:
            del self._holdings[symbol]

        self._transactions.append(Transaction(
            transaction_type=TransactionType.SELL,
            amount=total_credit,
            symbol=symbol,
            quantity=quantity,
            share_price=price_per_share
        ))

        return {
            "symbol": symbol,
            "quantity": quantity,
            "price_per_share": price_per_share,
            "total_credit": total_credit,
        }

    def get_portfolio_value(self) -> float:
        """Calculates the total value of the account (cash + holdings)."""
        holdings_value = 0.0
        for symbol, quantity in self._holdings.items():
            try:
                holdings_value += get_share_price(symbol) * quantity
            except InvalidSymbolError:
                # If a stock is delisted, its value is 0 for this calculation
                continue
        return self._cash_balance + holdings_value

    def get_profit_loss(self) -> float:
        """Calculates profit or loss based on total deposits."""
        if self._total_deposits == 0:
            return 0.0
        current_value = self.get_portfolio_value()
        return current_value - self._total_deposits

    def get_holdings_summary(self) -> List[Dict]:
        """Generates a summary of current holdings."""
        summary = []
        for symbol, quantity in self._holdings.items():
            try:
                price = get_share_price(symbol)
                value = price * quantity
            except InvalidSymbolError:
                price = "N/A"
                value = "N/A"
            
            summary.append({
                "Symbol": symbol,
                "Quantity": quantity,
                "Current Price": f"${price:,.2f}" if isinstance(price, float) else price,
                "Market Value": f"${value:,.2f}" if isinstance(value, float) else value,
            })
        return summary

    def get_transaction_history(self) -> List[Dict]:
        """Returns the formatted transaction history."""
        return [tx.to_dict() for tx in reversed(self._transactions)]
```

## 3. Gradio Frontend Design

### 3.1. UI Component Mapping

| Backend Method/Property | User Action | Gradio Input Components | Gradio Trigger Component | Gradio Output Components |
| :--- | :--- | :--- | :--- | :--- |
| `account.deposit` | Deposit funds | `amount_input` | `deposit_btn` | `cash_balance_display`, `status_md` |
| `account.withdraw` | Withdraw funds | `amount_input` | `withdraw_btn` | `cash_balance_display`, `status_md` |
| `account.buy_shares` | Buy shares | `symbol_input`, `quantity_input` | `buy_btn` | `trade_cash_display`, `trade_status_md` |
| `account.sell_shares` | Sell shares | `symbol_input`, `quantity_input` | `sell_btn` | `trade_cash_display`, `trade_status_md` |
| `account.cash_balance` | Page Load/Refresh | - | (Implicit on update) | `cash_balance_display`, `trade_cash_display` |
| `services.get_share_price` | Update Symbol/Qty | `symbol_input`, `quantity_input` | `.change()` / `.blur()` events | `current_price_display`, `estimated_cost_display` |

### 3.2. User-Facing Messages

#### Status Message Formatting
All status messages will be displayed in a `gr.Markdown` component. Success messages will be prefixed with `✅` and styled green. Error messages will be prefixed with `❌` and styled red.

**Example Implementation:**
```python
def format_success(message):
    return f"<p style='color:green;'>✅ Success: {message}</p>"

def format_error(message):
    return f"<p style='color:red;'>❌ Error: {message}</p>"
```

#### Message List

| User Story | Message Type | Trigger Condition | Message Template |
| :--- | :--- | :--- | :--- |
| **PORT-001** | Success | `account.deposit()` returns | `Successfully deposited ${amount}. Your new cash balance is ${new_balance}.` |
| **PORT-001** | Success | `account.withdraw()` returns | `Successfully withdrew ${amount}. Your new cash balance is ${new_balance}.` |
| **PORT-001** | Error | `amount` input is `None` or empty | `Please enter an amount to deposit or withdraw.` |
| **PORT-001** | Error | `InvalidAmountError` raised | `Amount must be a positive number.` |
| **PORT-001** | Error | `InsufficientFundsError` raised | `Insufficient funds for withdrawal. {exception_message}` |
| **PORT-001** | Error | Any other `Exception` | `The transaction could not be completed due to a system error. Please try again later.` |
| **PORT-002** | Success | `account.buy_shares()` returns | `Purchased {quantity} shares of {symbol} at ${price_per_share}. Total cost: ${total_cost}.` |
| **PORT-002** | Success | `account.sell_shares()` returns | `Sold {quantity} shares of {symbol} at ${price_per_share}. Total credit: ${total_credit}.` |
| **PORT-002** | Error | `InvalidAmountError` raised | `Quantity must be a positive whole number.` |
| **PORT-002** | Error | `InsufficientFundsError` raised | `Insufficient funds to buy {quantity} shares of {symbol}. {exception_message}` |
| **PORT-002** | Error | `InsufficientSharesError` raised | `Cannot sell {quantity} shares of {symbol}. {exception_message}` |
| **PORT-002** | Error | `InvalidSymbolError` raised | `{exception_message}` |
| **PORT-002** | Error | Any other `Exception` | `The trade could not be completed due to a system error. Please try again later.` |


### 3.3. UI Layout & Workflow (`app.py`)

The application will be structured using `gr.Blocks`.

```python
import gradio as gr
from accounts.account import Account, InvalidAmountError, InsufficientFundsError, InsufficientSharesError, InvalidSymbolError
from accounts.services import get_share_price

# --- App State ---
# A single account instance is created for the app's lifecycle
user_account = Account(owner="SimUser", initial_deposit=10000.00)

# --- UI Layout ---
with gr.Blocks(title="Trading Simulation Platform") as demo:
    gr.Markdown("# Trading Simulation Platform")
    
    with gr.Tabs():
        # Placeholder Tab 1
        with gr.Tab(label="Portfolio Dashboard"):
            gr.Markdown("## Dashboard (Coming Soon)")
            # ... Components for PORT-003 ...

        # Execute Trade Tab (PORT-002)
        with gr.Tab(label="Execute Trade"):
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("## Execute a Trade")
                    trade_cash_display = gr.Number(
                        label="Cash Available",
                        value=user_account.cash_balance,
                        interactive=False
                    )
                    symbol_input = gr.Textbox(label="Stock Symbol", placeholder="e.g., AAPL")
                    quantity_input = gr.Number(label="Quantity", minimum=1, precision=0)
                    with gr.Row():
                        buy_btn = gr.Button("Buy", variant="primary")
                        sell_btn = gr.Button("Sell", variant="stop")
                with gr.Column(scale=1):
                    current_price_display = gr.Number(label="Current Price", interactive=False)
                    estimated_cost_display = gr.Number(label="Estimated Cost/Value", interactive=False)
            trade_status_md = gr.Markdown(label="Status")

        # Manage Funds Tab (PORT-001)
        with gr.Tab(label="Manage Funds"):
            gr.Markdown("## Manage Your Funds")
            cash_balance_display = gr.Number(
                label="Current Cash Balance",
                value=user_account.cash_balance,
                interactive=False
            )
            amount_input = gr.Number(label="Amount", minimum=0.01)
            with gr.Row():
                deposit_btn = gr.Button("Deposit")
                withdraw_btn = gr.Button("Withdraw")
            status_md = gr.Markdown(label="Status")
        
        # Placeholder Tab 4
        with gr.Tab(label="History"):
            gr.Markdown("## Transaction History (Coming Soon)")
            # ... Components for PORT-004 ...
    
    # --- Event Handlers (Defined in Integration Section) ---

# demo.launch()
```

### 3.4. Input Validation & Error Display

*   **Client-Side:** Basic validation is handled by Gradio components (e.g., `gr.Number(minimum=0.01)`). This provides immediate feedback but is not sufficient for security.
*   **Server-Side:** All inputs are rigorously validated by the `Account` class methods. This is the authoritative source of validation.
*   **Error Display:** All error messages, whether from client-side checks or backend exceptions, will be formatted and rendered in the respective `status_md` or `trade_status_md` Markdown components.

## 4. Integration Points

### 4.1. Backend-Frontend Communication

Integration is achieved through handler functions that connect Gradio events to the backend `user_account` instance. These handlers manage the `try...except` block, format messages, and return a dictionary or tuple of `gr.update()` values.

### 4.2. Data Flow Diagram (Buy Share Example)

```
[User] -> Enters 'AAPL', '10' in `symbol_input`, `quantity_input`
  |
  v
[Gradio UI] -> Clicks `buy_btn`
  |
  v
[Gradio Event] -> Triggers `handle_buy(symbol='AAPL', quantity=10)`
  |
  v
[Handler Func] -> Calls `user_account.buy_shares(symbol='AAPL', quantity=10)`
  |
  +-- (Success Path) --> [Account Class] -> Updates balance/holdings. Returns tx details.
  |                            |
  |                            v
  |                        [Handler Func] -> Formats success message: "✅ Success: Purchased 10 shares..."
  |                            |
  |                            v
  |                        `return { trade_cash_display: gr.update(value=8497.50), trade_status_md: gr.update(value=msg) }`
  |
  +-- (Error Path)   --> [Account Class] -> `raise InsufficientFundsError(...)`
                             |
                             v
                         [Handler Func] -> `except InsufficientFundsError as e:` -> Formats error message: "❌ Error: Insufficient funds..."
                             |
                             v
                         `return { trade_status_md: gr.update(value=error_msg) }` // Other components don't update
  |
  v
[Gradio UI] -> Updates `trade_cash_display` and `trade_status_md` with new values.
  |
  v
[User] -> Sees updated balance and status message.
```

## 5. Implementation Examples

### 5.1. Backend Usage Example (`pytest` test case)

```python
# tests/test_account.py
import pytest
from accounts.account import Account, InsufficientFundsError

def test_successful_withdrawal():
    acc = Account(owner="test", initial_deposit=1000)
    new_balance = acc.withdraw(200)
    assert new_balance == 800
    assert acc.cash_balance == 800

def test_withdrawal_insufficient_funds():
    acc = Account(owner="test", initial_deposit=100)
    with pytest.raises(InsufficientFundsError):
        acc.withdraw(150)
    assert acc.cash_balance == 100
```

### 5.2. Frontend Integration Example (Handler Function)

This code would be placed within the `app.py` file.

```python
# --- Message Formatting Helpers ---
def format_success(message):
    return gr.Markdown(f"<p style='color:green;font-weight:bold;'>✅ Success: {message}</p>")

def format_error(message):
    return gr.Markdown(f"<p style='color:red;font-weight:bold;'>❌ Error: {message}</p>")

# --- Event Handler for Manage Funds Tab ---
def handle_deposit(amount):
    if not amount or amount <= 0:
        return {
            status_md: format_error("Please enter a positive amount to deposit."),
        }
    try:
        new_balance = user_account.deposit(amount)
        success_msg = f"Successfully deposited ${amount:,.2f}. Your new cash balance is ${new_balance:,.2f}."
        return {
            cash_balance_display: gr.update(value=new_balance),
            trade_cash_display: gr.update(value=new_balance),
            status_md: format_success(success_msg),
            amount_input: gr.update(value=None) # Clear input field
        }
    except Exception as e:
        # Generic catch-all for unexpected errors
        return {status_md: format_error("The transaction could not be completed due to a system error.")}

# --- Wiring the handler to the UI ---
# (Inside the gr.Blocks context)
deposit_btn.click(
    fn=handle_deposit,
    inputs=[amount_input],
    outputs=[cash_balance_display, trade_cash_display, status_md, amount_input]
)

# ... similar handler for withdraw, buy, sell ...
```

## 6. Testing & QA Guidelines

### 6.1. Backend Unit Testing (`pytest`)

*   Create test cases for every public method in `Account`.
*   For each method, test at least one success scenario.
*   For methods that can fail, test every defined exception path (e.g., `test_buy_raises_insufficient_funds`, `test_sell_raises_insufficient_shares`).
*   Test edge cases: zero/negative values, selling all shares of a stock.
*   Verify that internal state (`_cash_balance`, `_holdings`, `_transactions`) is updated correctly after each operation.

### 6.2. End-to-End QA Validation

QA should execute all Gherkin scenarios defined in the user stories **verbatim**.

**Key Validation Points for `PORT-001: Manage Funds`:**
1.  **Given** balance is $1000, **When** depositing $500, **Then** balance display must update to $1500 and success message must appear.
2.  **Given** balance is $1000, **When** withdrawing $1500, **Then** balance must *not* change, and the "Insufficient funds" error message must appear.
3.  **When** entering "-50" in amount and clicking deposit/withdraw, **Then** the "Amount must be a positive number" error must appear.
4.  **When** the amount field is empty and a button is clicked, **Then** the "Please enter an amount" error must appear.
5.  Verify that the cash balance display in the "Execute Trade" tab also updates after a deposit or withdrawal.

**Key Validation Points for `PORT-002: Execute Trade`:**
1.  **When** typing "AAPL" into the symbol box, **Then** "Current Price" must update to `$150.25`.
2.  **When** typing "10" into quantity, **Then** "Estimated Cost" must update to `$1,502.50`.
3.  **Given** sufficient funds, **When** buying 10 shares of AAPL, **Then** "Cash Available" must decrease by $1,502.50 and the correct success message must be shown.
4.  **Given** owning 5 shares of TSLA, **When** attempting to sell 10, **Then** cash and holdings must *not* change, and the "Cannot sell 10 shares... You only own 5" error must be displayed.
5.  **When** entering an invalid symbol like "FAKE" and clicking buy, **Then** the "Stock symbol 'FAKE' is not valid" error must be shown.