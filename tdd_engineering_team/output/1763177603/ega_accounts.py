"""
Manages a user's trading account, including cash, holdings, and transactions.

This module provides the core business logic for a trading simulation platform.
It is designed to be completely self-contained and independent of any UI
framework, making it easily testable and reusable.

Primary Components:
- AccountError (and subclasses): Custom exceptions for specific business rule
  violations like insufficient funds or invalid stock symbols.
- TypedDicts (Transaction, PortfolioSummary, etc.): Clear data structures
  for representing financial data.
- Account: The main class that encapsulates all state and operations for a
  single user's account.

Usage Example:
    # This requires a price provider function. For this example, we'll
    # create a simple one. In a real application, this would fetch data
    # from an external API.
    def get_price(symbol: str) -> float | None:
        prices = {"AAPL": 150.0, "TSLA": 300.0}
        return prices.get(symbol.upper())

    try:
        # Create a new account
        my_account = Account(
            username='trader123',
            initial_deposit=10000.00,
            price_provider=get_price
        )
        print(f"Account created. Balance: ${my_account.cash_balance:,.2f}")

        # Deposit funds
        my_account.deposit(2000)
        print(f"Deposited. New Balance: ${my_account.cash_balance:,.2f}")

        # Buy shares
        buy_result = my_account.buy_shares('AAPL', 10)
        print(f"Bought shares. Cost: ${buy_result['total_cost']}. New Balance: ${my_account.cash_balance:,.2f}")

        # View portfolio summary
        summary = my_account.get_portfolio_summary()
        print(f"Portfolio Value: ${summary['total_portfolio_value']:,.2f}")
        print(f"Profit/Loss: ${summary['profit_loss']:,.2f}")

        # View transaction history
        history = my_account.get_transaction_history()
        print("\\n--- Transaction History ---")
        for tx in history:
            print(f"{tx['timestamp']:%Y-%m-%d %H:%M} | {tx['type']:<10} | ${tx['total_amount']:>9,.2f}")

    except (AccountError, ValueError) as e:
        print(f"\\nERROR: {e}")
"""

from collections import defaultdict
from datetime import datetime
from typing import (
    Callable, Dict, List, Literal, Optional, TypedDict
)

# --- Data Models/Schemas ---

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
    net_deposits: float
    holdings_with_prices: List[Dict[str, float | int | str]]
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


# --- Primary Account Class ---

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
            price_provider: A function that takes a symbol string and returns a
                            price float or None.

        Raises:
            ValueError: If the initial deposit is not a positive number.
        """
        if not isinstance(initial_deposit, (int, float)) or initial_deposit <= 0:
            raise ValueError("Initial deposit must be a positive number.")

        self.username: str = username
        self.cash_balance: float = initial_deposit
        self.holdings: Dict[str, int] = defaultdict(int)
        self.transactions: List[Transaction] = []
        self._price_provider: Callable[[str], Optional[float]] = price_provider

        self._record_transaction(
            type="DEPOSIT",
            total_amount=initial_deposit
        )

    def deposit(self, amount: float) -> float:
        """
        Adds funds to the account's cash balance.

        Args:
            amount: The amount to deposit.

        Returns:
            The new cash balance after the deposit.

        Raises:
            ValueError: If the amount is not a positive number.
        """
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be a positive number.")
        self.cash_balance += amount
        self._record_transaction(type="DEPOSIT", total_amount=amount)
        return self.cash_balance

    def withdraw(self, amount: float) -> float:
        """
        Removes funds from the account's cash balance.

        Args:
            amount: The amount to withdraw.

        Returns:
            The new cash balance after the withdrawal.

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
        self._record_transaction(type="WITHDRAWAL", total_amount=amount)
        return self.cash_balance

    def buy_shares(self, symbol: str, quantity: int) -> Dict:
        """
        Purchases shares of a stock, deducting the cost from the cash balance.

        Args:
            symbol: The stock symbol to buy (e.g., 'AAPL').
            quantity: The number of shares to buy.

        Returns:
            A dictionary with details of the successful transaction.

        Raises:
            ValueError: If quantity is not a positive integer.
            InvalidSymbolError: If the symbol is not valid or has no price.
            InsufficientFundsError: If the total cost exceeds the cash balance.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive whole number.")

        clean_symbol = symbol.upper().strip()
        price = self._price_provider(clean_symbol)
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
            "BUY", total_cost, symbol=clean_symbol,
            quantity=quantity, price_per_share=price
        )

        return {
            'symbol': clean_symbol, 'quantity': quantity,
            'price_per_share': price, 'total_cost': total_cost
        }

    def sell_shares(self, symbol: str, quantity: int) -> Dict:
        """
        Sells shares of a stock, adding the proceeds to the cash balance.

        Args:
            symbol: The stock symbol to sell.
            quantity: The number of shares to sell.

        Returns:
            A dictionary with details of the successful transaction.

        Raises:
            ValueError: If quantity is not a positive integer.
            InvalidSymbolError: If the symbol is not valid or has no price.
            InsufficientSharesError: If trying to sell more shares than owned.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive whole number.")

        clean_symbol = symbol.upper().strip()
        owned_quantity = self.holdings.get(clean_symbol, 0)
        if quantity > owned_quantity:
            raise InsufficientSharesError(
                f"Insufficient shares. You cannot sell {quantity} shares of "
                f"{clean_symbol} as you only own {owned_quantity}."
            )

        price = self._price_provider(clean_symbol)
        if price is None:
            # This is an edge case, as a user shouldn't be able to own a stock
            # with an invalid symbol, but it's good practice to check.
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
            "SELL", total_proceeds, symbol=clean_symbol,
            quantity=quantity, price_per_share=price
        )

        return {
            'symbol': clean_symbol, 'quantity': quantity,
            'price_per_share': price, 'total_proceeds': total_proceeds
        }

    def get_portfolio_summary(self) -> PortfolioSummary:
        """
        Calculates a full summary of the account's current state and performance.

        Returns:
            A PortfolioSummary TypedDict with all calculated values.
        """
        total_shares_value = 0.0
        holdings_with_prices = []
        for symbol, quantity in self.holdings.items():
            price = self._price_provider(symbol) or 0.0
            value = quantity * price
            total_shares_value += value
            holdings_with_prices.append({
                "symbol": symbol, "quantity": quantity,
                "price": price, "value": value
            })

        net_deposits = (
            sum(tx['total_amount'] for tx in self.transactions if tx['type'] == 'DEPOSIT') -
            sum(tx['total_amount'] for tx in self.transactions if tx['type'] == 'WITHDRAWAL')
        )

        total_portfolio_value = self.cash_balance + total_shares_value
        profit_loss = total_portfolio_value - net_deposits

        return {
            "cash_balance": self.cash_balance,
            "net_deposits": net_deposits,
            "holdings_with_prices": holdings_with_prices,
            "total_portfolio_value": total_portfolio_value,
            "total_shares_value": total_shares_value,
            "profit_loss": profit_loss
        }

    def get_transaction_history(self) -> List[Transaction]:
        """
        Retrieves the full list of transactions for the account.

        Returns:
            A list of Transaction objects, sorted from most to least recent.
        """
        return sorted(self.transactions, key=lambda tx: tx['timestamp'], reverse=True)

    def _record_transaction(
        self,
        type: TransactionType,
        total_amount: float,
        symbol: Optional[str] = None,
        quantity: Optional[int] = None,
        price_per_share: Optional[float] = None
    ):
        """A private helper to create and log a transaction."""
        transaction: Transaction = {
            "timestamp": datetime.now(),
            "type": type,
            "symbol": symbol,
            "quantity": quantity,
            "price_per_share": price_per_share,
            "total_amount": total_amount
        }
        self.transactions.append(transaction)