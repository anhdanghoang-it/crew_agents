"""
accounts.py - Core backend module for the Trading Simulation Platform.

This module provides the `Account` class, which encapsulates all business logic
for managing a user's trading account. It handles cash deposits, withdrawals,
share trading (buying/selling), and portfolio reporting.

The module is designed to be self-contained and independent of the user
interface, allowing for easy testing and integration with various frontends,
such as Gradio.

Key Components:
- Custom Exceptions:
    - AccountError: Base class for account-related issues.
    - InsufficientFundsError: For operations that fail due to lack of cash.
    - InsufficientSharesError: For selling more shares than owned.
    - InvalidSymbolError: For trades involving non-existent stock symbols.
- Data Models (TypedDict):
    - Transaction: Represents a single financial transaction.
    - Holding: Represents the quantity of a single stock owned.
    - PortfolioSummary: A complete snapshot of the account's value.
- Account Class:
    - The central class managing state, including cash balance, share
      holdings, and transaction history.
    - Provides methods for all user actions (`deposit`, `buy_shares`, etc.).
    - Returns structured data suitable for UI consumption.

Usage Example:
    # This assumes a pricing function `get_share_price` is available.
    # from pricing import get_share_price

    try:
        # Create a new account
        my_account = Account(
            username='trader123',
            initial_deposit=10000.00,
            price_provider=get_share_price
        )
        print(f"Account created for trader123 with ${my_account.cash_balance:,.2f}")

        # Deposit funds
        my_account.deposit(5000.00)
        print(f"New balance: ${my_account.cash_balance:,.2f}")

        # Buy shares
        buy_info = my_account.buy_shares(symbol='AAPL', quantity=10)
        print(f"Bought {buy_info['quantity']} AAPL shares.")
        print(f"Remaining cash: ${my_account.cash_balance:,.2f}")

        # View portfolio
        summary = my_account.get_portfolio_summary()
        print(f"Total portfolio value: ${summary['total_portfolio_value']:,.2f}")
        print(f"Profit/Loss: ${summary['profit_loss']:,.2f}")

        # View transaction history
        history = my_account.get_transaction_history()
        print("--- Transaction History ---")
        for tx in history:
            print(f"{tx['timestamp']}: {tx['type']} - ${tx['total_amount']:,.2f}")

    except (AccountError, ValueError) as e:
        print(f"Error: {e}")
"""

from collections import defaultdict
from datetime import datetime
from typing import TypedDict, Literal, List, Dict, Callable, Optional

# --- Data Models and Types ---

TransactionType = Literal["DEPOSIT", "WITHDRAWAL", "BUY", "SELL"]


class Transaction(TypedDict):
    """Represents a single financial transaction."""
    timestamp: datetime
    type: TransactionType
    symbol: Optional[str]
    quantity: Optional[int]
    price_per_share: Optional[float]
    total_amount: float


class Holding(TypedDict):
    """Represents the quantity of a single stock owned."""
    symbol: str
    quantity: int


class PortfolioSummary(TypedDict):
    """A snapshot of the account's entire value and performance."""
    cash_balance: float
    total_deposits: float
    holdings: List[Holding]
    total_portfolio_value: float
    total_shares_value: float
    profit_loss: float


# --- Custom Exceptions ---

class AccountError(Exception):
    """Base exception for all account-related errors."""
    pass


class InsufficientFundsError(AccountError):
    """Raised when an operation cannot be completed due to lack of cash."""
    pass


class InsufficientSharesError(AccountError):
    """Raised when trying to sell more shares than owned."""
    pass


class InvalidSymbolError(AccountError):
    """Raised when a stock symbol is not valid or has no price."""
    pass


# --- Main Account Class ---

class Account:
    """
    Manages a user's trading account, including cash, holdings, and transactions.
    """

    def __init__(
        self,
        username: str,
        initial_deposit: float,
        price_provider: Callable[[str], Optional[float]]
    ):
        """
        Initializes a new trading account.

        Args:
            username: The user's chosen name.
            initial_deposit: The starting cash balance.
            price_provider: A function that takes a symbol and returns a price.

        Raises:
            ValueError: If the initial deposit is not a positive number.
        """
        if not isinstance(initial_deposit, (int, float)) or initial_deposit <= 0:
            raise ValueError("Initial deposit must be a positive number.")

        self.username: str = username
        self.cash_balance: float = initial_deposit
        self.price_provider: Callable[[str], Optional[float]] = price_provider
        self.holdings: Dict[str, int] = defaultdict(int)
        self.transactions: List[Transaction] = []

        # Record the initial deposit transaction
        self._record_transaction(
            tx_type="DEPOSIT",
            total_amount=initial_deposit
        )

    def _record_transaction(
        self,
        tx_type: TransactionType,
        total_amount: float,
        symbol: Optional[str] = None,
        quantity: Optional[int] = None,
        price_per_share: Optional[float] = None
    ) -> None:
        """
        A helper method to create and log a transaction.

        Args:
            tx_type: The type of transaction.
            total_amount: The total cash value of the transaction.
            symbol: The stock symbol, if applicable.
            quantity: The number of shares, if applicable.
            price_per_share: The price per share, if applicable.
        """
        transaction: Transaction = {
            "timestamp": datetime.now(),
            "type": tx_type,
            "symbol": symbol,
            "quantity": quantity,
            "price_per_share": price_per_share,
            "total_amount": total_amount
        }
        self.transactions.append(transaction)

    def deposit(self, amount: float) -> float:
        """
        Adds funds to the account's cash balance.

        Args:
            amount: The amount to deposit.

        Returns:
            The new cash balance.

        Raises:
            ValueError: If the amount is not a positive number.
        """
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be a positive number.")

        self.cash_balance += amount
        self._record_transaction(tx_type="DEPOSIT", total_amount=amount)
        return self.cash_balance

    def withdraw(self, amount: float) -> float:
        """
        Removes funds from the account's cash balance.

        Args:
            amount: The amount to withdraw.

        Returns:
            The new cash balance.

        Raises:
            ValueError: If the amount is not a positive number.
            InsufficientFundsError: If withdrawal amount exceeds cash balance.
        """
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be a positive number.")

        if amount > self.cash_balance:
            raise InsufficientFundsError(
                f"Insufficient funds. You cannot withdraw more than your "
                f"available cash balance of ${self.cash_balance:,.2f}."
            )

        self.cash_balance -= amount
        self._record_transaction(tx_type="WITHDRAWAL", total_amount=amount)
        return self.cash_balance

    def buy_shares(self, symbol: str, quantity: int) -> Dict[str, any]:
        """
        Purchases shares of a stock, deducting the cost from the cash balance.

        Args:
            symbol: The stock symbol to buy (e.g., 'AAPL').
            quantity: The number of shares to buy.

        Returns:
            A dictionary with details of the successful transaction.

        Raises:
            ValueError: If quantity is not a positive integer.
            InvalidSymbolError: If the symbol is not valid.
            InsufficientFundsError: If the total cost exceeds the cash balance.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive whole number.")
        if not symbol or not isinstance(symbol, str):
            raise InvalidSymbolError("A valid stock symbol must be provided.")

        clean_symbol = symbol.upper().strip()
        price = self.price_provider(clean_symbol)

        if price is None:
            raise InvalidSymbolError(
                f"Invalid stock symbol '{symbol}'. Please use a valid "
                "symbol (e.g., AAPL, TSLA, GOOGL)."
            )

        total_cost = quantity * price
        if total_cost > self.cash_balance:
            raise InsufficientFundsError(
                f"Insufficient funds. You need ${total_cost:,.2f} to buy "
                f"{quantity} shares of {clean_symbol}, but you only have "
                f"${self.cash_balance:,.2f}."
            )

        self.cash_balance -= total_cost
        self.holdings[clean_symbol] += quantity
        self._record_transaction(
            tx_type="BUY",
            symbol=clean_symbol,
            quantity=quantity,
            price_per_share=price,
            total_amount=total_cost
        )

        return {
            "symbol": clean_symbol,
            "quantity": quantity,
            "price_per_share": price,
            "total_cost": total_cost,
        }

    def sell_shares(self, symbol: str, quantity: int) -> Dict[str, any]:
        """
        Sells shares of a stock, adding the proceeds to the cash balance.

        Args:
            symbol: The stock symbol to sell.
            quantity: The number of shares to sell.

        Returns:
            A dictionary with details of the successful transaction.

        Raises:
            ValueError: If quantity is not a positive integer.
            InvalidSymbolError: If the symbol is not valid.
            InsufficientSharesError: If trying to sell more shares than owned.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive whole number.")
        if not symbol or not isinstance(symbol, str):
            raise InvalidSymbolError("A valid stock symbol must be provided.")

        clean_symbol = symbol.upper().strip()
        owned_quantity = self.holdings.get(clean_symbol, 0)

        if quantity > owned_quantity:
            raise InsufficientSharesError(
                f"Insufficient shares. You cannot sell {quantity} shares of "
                f"{clean_symbol} as you only own {owned_quantity}."
            )

        price = self.price_provider(clean_symbol)
        if price is None:
            raise InvalidSymbolError(
                f"Invalid stock symbol '{symbol}'. Please use a valid "
                "symbol (e.g., AAPL, TSLA, GOOGL)."
            )

        total_proceeds = quantity * price
        self.cash_balance += total_proceeds
        self.holdings[clean_symbol] -= quantity
        if self.holdings[clean_symbol] == 0:
            del self.holdings[clean_symbol]

        self._record_transaction(
            tx_type="SELL",
            symbol=clean_symbol,
            quantity=quantity,
            price_per_share=price,
            total_amount=total_proceeds
        )

        return {
            "symbol": clean_symbol,
            "quantity": quantity,
            "price_per_share": price,
            "total_proceeds": total_proceeds
        }

    def get_portfolio_summary(self) -> PortfolioSummary:
        """
        Calculates a full summary of the account's current state and performance.

        Returns:
            A PortfolioSummary object with all calculated values.
        """
        total_shares_value = 0.0
        current_holdings: List[Holding] = []

        for symbol, quantity in self.holdings.items():
            price = self.price_provider(symbol)
            # If price is None, we can't value it. Assume 0 for calculation.
            current_value = (price * quantity) if price is not None else 0.0
            total_shares_value += current_value
            current_holdings.append({"symbol": symbol, "quantity": quantity})

        total_portfolio_value = self.cash_balance + total_shares_value
        total_deposits = sum(
            tx['total_amount'] for tx in self.transactions if tx['type'] == 'DEPOSIT'
        )
        profit_loss = total_portfolio_value - total_deposits

        summary: PortfolioSummary = {
            "cash_balance": self.cash_balance,
            "total_deposits": total_deposits,
            "holdings": current_holdings,
            "total_shares_value": total_shares_value,
            "total_portfolio_value": total_portfolio_value,
            "profit_loss": profit_loss,
        }
        return summary

    def get_transaction_history(self) -> List[Transaction]:
        """
        Retrieves the full list of transactions for the account.

        Returns:
            A list of Transaction objects, sorted from most to least recent.
        """
        return sorted(
            self.transactions, key=lambda t: t['timestamp'], reverse=True
        )


if __name__ == '__main__':
    # This block provides a simple, self-contained test and usage demonstration.
    # It requires a `pricing.py` file in the same directory with `get_share_price`.

    # A mock pricing function for demonstration purposes
    def get_mock_share_price(symbol: str) -> Optional[float]:
        """Mock price provider for testing."""
        prices = {"AAPL": 150.00, "TSLA": 300.00, "GOOGL": 2200.00}
        return prices.get(symbol.upper())

    print("--- Running Backend Demonstration ---")
    try:
        # US-001: Account Creation
        print("\n[US-001] Creating account...")
        my_account = Account(
            username='trader123',
            initial_deposit=10000.00,
            price_provider=get_mock_share_price
        )
        print(f"Success: Account 'trader123' created with an initial deposit of ${my_account.cash_balance:,.2f}.")

        # US-002: Deposit
        print("\n[US-002] Depositing funds...")
        new_balance = my_account.deposit(2000)
        print(f"Success: $2,000.00 deposited. New balance is ${new_balance:,.2f}.")

        # US-003: Buy Shares
        print("\n[US-003] Buying shares...")
        buy_result = my_account.buy_shares('AAPL', 10)
        price = buy_result['price_per_share']
        cost = buy_result['total_cost']
        print(f"Success: Bought 10 shares of AAPL at ${price:,.2f} each for a total of ${cost:,.2f}.")
        print(f"Remaining cash: ${my_account.cash_balance:,.2f}")

        # US-003: Sell Shares
        print("\n[US-003] Selling shares...")
        get_mock_share_price = lambda s: 160.00 if s == "AAPL" else 300.00
        my_account.price_provider = get_mock_share_price
        sell_result = my_account.sell_shares('AAPL', 5)
        price = sell_result['price_per_share']
        proceeds = sell_result['total_proceeds']
        print(f"Success: Sold 5 shares of AAPL at ${price:,.2f} each for a total of ${proceeds:,.2f}.")
        print(f"New cash balance: ${my_account.cash_balance:,.2f}")

        # US-004: View Portfolio
        print("\n[US-004] Getting portfolio summary...")
        summary = my_account.get_portfolio_summary()
        print(f"  Cash Balance: ${summary['cash_balance']:,.2f}")
        print(f"  Total Deposits: ${summary['total_deposits']:,.2f}")
        print(f"  Holdings: {summary['holdings']}")
        print(f"  Total Shares Value: ${summary['total_shares_value']:,.2f}")
        print(f"  Total Portfolio Value: ${summary['total_portfolio_value']:,.2f}")
        print(f"  Profit/Loss: ${summary['profit_loss']:,.2f}")

        # US-004: View History
        print("\n[US-004] Getting transaction history...")
        history = my_account.get_transaction_history()
        for tx in history:
            details = f"Type: {tx['type']}, Amount: ${tx['total_amount']:,.2f}"
            if tx['symbol']:
                details += f", Symbol: {tx['symbol']}, Qty: {tx['quantity']}"
            print(f"  - {tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | {details}")

        # --- Error Handling Demonstrations ---
        print("\n--- Testing Error Conditions ---")

        # Insufficient Funds (Withdrawal)
        try:
            print("\nAttempting to withdraw more than available cash...")
            my_account.withdraw(999999)
        except InsufficientFundsError as e:
            print(f"Caught expected error: {e}")

        # Insufficient Funds (Buy)
        try:
            print("\nAttempting to buy shares with insufficient funds...")
            my_account.buy_shares('GOOGL', 10)
        except InsufficientFundsError as e:
            print(f"Caught expected error: {e}")

        # Insufficient Shares (Sell)
        try:
            print("\nAttempting to sell more shares than owned...")
            my_account.sell_shares('AAPL', 99)
        except InsufficientSharesError as e:
            print(f"Caught expected error: {e}")

        # Invalid Symbol
        try:
            print("\nAttempting to trade an invalid symbol...")
            my_account.buy_shares('XYZ', 1)
        except InvalidSymbolError as e:
            print(f"Caught expected error: {e}")

        # Invalid Amount
        try:
            print("\nAttempting to deposit a negative amount...")
            my_account.deposit(-100)
        except ValueError as e:
            print(f"Caught expected error: {e}")

    except (AccountError, ValueError) as e:
        print(f"\nAn unexpected error occurred during the demonstration: {e}")