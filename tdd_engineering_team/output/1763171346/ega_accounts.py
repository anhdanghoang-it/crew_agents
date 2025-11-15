```python
"""
accounts.py: A self-contained module for managing trading simulation accounts.

This module provides the `Account` class, which encapsulates all the business
logic for a user's trading account. It handles cash management (deposits,
withdrawals), share trading (buying, selling), and portfolio reporting.

The module is designed to be independent of the user interface, making it
easily testable and integrable with various frontends like Gradio. It relies
on an injectable price provider function to fetch share prices, decoupling it
from any specific market data source.

Core functionalities include:
- Account creation with an initial deposit.
- Depositing and withdrawing cash.
- Buying and selling shares of stock.
- Calculating portfolio summary including total value and profit/loss.
- Maintaining a detailed transaction history.

Custom exceptions are used to signal specific business rule violations,
allowing the calling application to provide clear, user-friendly feedback.

Example Usage:

    # In a separate file, e.g., main.py
    from accounts import Account, AccountError
    
    # A simple price provider function (can be replaced with a real API call)
    def get_share_price(symbol: str) -> float | None:
        prices = {"AAPL": 150.00, "TSLA": 300.00}
        return prices.get(symbol.upper())

    try:
        # 1. Create an account (US-001)
        my_account = Account(
            username='trader123',
            initial_deposit=10000.00,
            price_provider=get_share_price
        )
        print(f"Account for {my_account.username} created.")
        print(f"Initial balance: ${my_account.cash_balance:,.2f}")

        # 2. Deposit funds (US-002)
        my_account.deposit(2000.00)
        print(f"Deposited $2,000. New balance: ${my_account.cash_balance:,.2f}")

        # 3. Buy shares (US-003)
        buy_info = my_account.buy_shares('AAPL', 10)
        print(f"Bought {buy_info['quantity']} shares of {buy_info['symbol']}.")
        print(f"Remaining balance: ${my_account.cash_balance:,.2f}")

        # 4. View portfolio (US-004)
        summary = my_account.get_portfolio_summary()
        print(f"Portfolio Value: ${summary['total_portfolio_value']:,.2f}")
        print(f"Profit/Loss: ${summary['profit_loss']:,.2f}")
        print(f"Holdings: {summary['holdings']}")

        # 5. View transaction history (US-004)
        history = my_account.get_transaction_history()
        print("\\n--- Transaction History ---")
        for tx in history:
            print(f"{tx['timestamp']} | {tx['type']:<10} | "
                  f"Amount: ${tx['total_amount']:>8,.2f}")

    except (AccountError, ValueError) as e:
        print(f"An error occurred: {e}")
"""

from collections import defaultdict
from datetime import datetime
from typing import (
    TypedDict, Literal, List, Optional, Dict, Callable
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
    holdings: List[Holding]
    total_portfolio_value: float
    total_shares_value: float
    profit_loss: float


# --- Custom Exceptions for Error Handling ---

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
            price_provider: A function that takes a symbol string and returns
                            a price float or None.

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

    def _record_transaction(
        self,
        type: TransactionType,
        total_amount: float,
        symbol: Optional[str] = None,
        quantity: Optional[int] = None,
        price_per_share: Optional[float] = None
    ):
        """Internal helper to create, format, and log a transaction."""
        transaction: Transaction = {
            "timestamp": datetime.now(),
            "type": type,
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

    def buy_shares(self, symbol: str, quantity: int) -> Dict[str, any]:
        """
        Purchases shares of a stock, deducting cost from the cash balance.

        Args:
            symbol: The stock symbol to buy (e.g., 'AAPL').
            quantity: The number of shares to buy.

        Returns:
            A dictionary with details of the successful transaction:
            {'symbol': str, 'quantity': int, 'price_per_share': float,
             'total_cost': float}

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
            type="BUY",
            symbol=clean_symbol,
            quantity=quantity,
            price_per_share=price,
            total_amount=total_cost
        )
        return {
            'symbol': clean_symbol,
            'quantity': quantity,
            'price_per_share': price,
            'total_cost': total_cost
        }

    def sell_shares(self, symbol: str, quantity: int) -> Dict[str, any]:
        """
        Sells shares of a stock, adding proceeds to the cash balance.

        Args:
            symbol: The stock symbol to sell.
            quantity: The number of shares to sell.

        Returns:
            A dictionary with details of the successful transaction:
            {'symbol': str, 'quantity': int, 'price_per_share': float,
             'total_proceeds': float}

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
            type="SELL",
            symbol=clean_symbol,
            quantity=quantity,
            price_per_share=price,
            total_amount=total_proceeds
        )
        return {
            'symbol': clean_symbol,
            'quantity': quantity,
            'price_per_share': price,
            'total_proceeds': total_proceeds
        }

    def get_portfolio_summary(self) -> PortfolioSummary:
        """
        Calculates a full summary of the account's current state.

        This method provides a snapshot of the account's value, including
        cash balance, the market value of all share holdings, net deposits,
        and overall profit or loss.

        Returns:
            A PortfolioSummary TypedDict with all calculated values.
        """
        total_shares_value = 0.0
        holdings_list: List[Holding] = []
        for symbol, quantity in self.holdings.items():
            price = self._price_provider(symbol)
            if price is not None:
                total_shares_value += quantity * price
            # We still list the holding even if price is not available
            holdings_list.append({"symbol": symbol, "quantity": quantity})

        total_portfolio_value = self.cash_balance + total_shares_value

        net_deposits = sum(
            t['total_amount'] for t in self.transactions if t['type'] == 'DEPOSIT'
        ) - sum(
            t['total_amount'] for t in self.transactions if t['type'] == 'WITHDRAWAL'
        )

        profit_loss = total_portfolio_value - net_deposits

        return {
            "cash_balance": self.cash_balance,
            "net_deposits": net_deposits,
            "holdings": holdings_list,
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
        return sorted(
            self.transactions,
            key=lambda t: t['timestamp'],
            reverse=True
        )
```