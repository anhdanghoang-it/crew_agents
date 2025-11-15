"""
accounts.py - Core backend module for the Trading Simulation Platform.

This module provides the `Account` class, which encapsulates all business logic
for managing a user's trading account. It handles cash management (deposits,
withdrawals), trading operations (buying/selling shares), and reporting
(portfolio summary, transaction history).

The design is self-contained and independent of the UI layer, relying on an
injectable `price_provider` function for external market data. It uses custom
exceptions to signal specific business rule violations, allowing the calling
application to provide clear, user-friendly error messages.
"""

import time
from collections import defaultdict
from datetime import datetime
from typing import (Callable, Dict, List, Literal, Optional, TypedDict)

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
            tx_type='DEPOSIT',
            amount=initial_deposit
        )

    def _record_transaction(
        self,
        tx_type: TransactionType,
        amount: float,
        symbol: Optional[str] = None,
        quantity: Optional[int] = None,
        price: Optional[float] = None
    ) -> None:
        """A helper method to create and log a transaction."""
        # Use a slight delay to ensure unique timestamps for rapid transactions
        time.sleep(0.001)
        transaction: Transaction = {
            'timestamp': datetime.now(),
            'type': tx_type,
            'symbol': symbol,
            'quantity': quantity,
            'price_per_share': price,
            'total_amount': amount
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
        self._record_transaction(tx_type='DEPOSIT', amount=amount)
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
            msg = (
                "Insufficient funds. You cannot withdraw more than your "
                f"available cash balance of ${self.cash_balance:,.2f}."
            )
            raise InsufficientFundsError(msg)

        self.cash_balance -= amount
        self._record_transaction(tx_type='WITHDRAWAL', amount=amount)
        return self.cash_balance

    def buy_shares(self, symbol: str, quantity: int) -> Dict:
        """
        Purchases shares of a stock, deducting the cost from the cash balance.

        Args:
            symbol: The stock symbol to buy (e.g., 'AAPL').
            quantity: The number of shares to buy.

        Returns:
            A dictionary with details of the successful transaction:
            {'symbol': str, 'quantity': int, 'price_per_share': float, 'total_cost': float}

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
            msg = (
                f"Invalid stock symbol '{symbol}'. Please use a valid "
                "symbol (e.g., AAPL, TSLA, GOOGL)."
            )
            raise InvalidSymbolError(msg)

        total_cost = quantity * price
        if total_cost > self.cash_balance:
            msg = (
                f"Insufficient funds. You need ${total_cost:,.2f} to buy "
                f"{quantity} shares of {clean_symbol}, but you only have "
                f"${self.cash_balance:,.2f}."
            )
            raise InsufficientFundsError(msg)

        self.cash_balance -= total_cost
        self.holdings[clean_symbol] += quantity
        self._record_transaction(
            tx_type='BUY',
            amount=total_cost,
            symbol=clean_symbol,
            quantity=quantity,
            price=price
        )

        return {
            'symbol': clean_symbol,
            'quantity': quantity,
            'price_per_share': price,
            'total_cost': total_cost
        }

    def sell_shares(self, symbol: str, quantity: int) -> Dict:
        """
        Sells shares of a stock, adding the proceeds to the cash balance.

        Args:
            symbol: The stock symbol to sell.
            quantity: The number of shares to sell.

        Returns:
            A dictionary with details of the successful transaction:
            {'symbol': str, 'quantity': int, 'price_per_share': float, 'total_proceeds': float}

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
            msg = (
                f"Insufficient shares. You cannot sell {quantity} shares of "
                f"{clean_symbol} as you only own {owned_quantity}."
            )
            raise InsufficientSharesError(msg)

        price = self._price_provider(clean_symbol)
        if price is None:
            msg = (
                f"Invalid stock symbol '{symbol}'. Please use a valid "
                "symbol (e.g., AAPL, TSLA, GOOGL)."
            )
            raise InvalidSymbolError(msg)

        total_proceeds = quantity * price
        self.cash_balance += total_proceeds
        self.holdings[clean_symbol] -= quantity
        if self.holdings[clean_symbol] == 0:
            del self.holdings[clean_symbol]

        self._record_transaction(
            tx_type='SELL',
            amount=total_proceeds,
            symbol=clean_symbol,
            quantity=quantity,
            price=price
        )

        return {
            'symbol': clean_symbol,
            'quantity': quantity,
            'price_per_share': price,
            'total_proceeds': total_proceeds
        }

    def get_portfolio_summary(self) -> PortfolioSummary:
        """
        Calculates a full summary of the account's current state and performance.

        Returns:
            A PortfolioSummary TypedDict with all calculated values.
        """
        total_shares_value = 0.0
        holdings_list: List[Holding] = []
        for symbol, quantity in self.holdings.items():
            price = self._price_provider(symbol)
            if price is not None:
                total_shares_value += quantity * price
            holdings_list.append({'symbol': symbol, 'quantity': quantity})

        total_portfolio_value = self.cash_balance + total_shares_value

        total_deposits = sum(
            tx['total_amount'] for tx in self.transactions if tx['type'] == 'DEPOSIT'
        )
        total_withdrawals = sum(
            tx['total_amount'] for tx in self.transactions if tx['type'] == 'WITHDRAWAL'
        )
        net_deposits = total_deposits - total_withdrawals

        profit_loss = total_portfolio_value - net_deposits

        return {
            'cash_balance': self.cash_balance,
            'net_deposits': net_deposits,
            'holdings': sorted(holdings_list, key=lambda h: h['symbol']),
            'total_portfolio_value': total_portfolio_value,
            'total_shares_value': total_shares_value,
            'profit_loss': profit_loss
        }

    def get_transaction_history(self) -> List[Transaction]:
        """
        Retrieves the full list of transactions for the account.

        Returns:
            A list of Transaction objects, sorted from most to least recent.
        """
        return sorted(self.transactions, key=lambda tx: tx['timestamp'], reverse=True)


if __name__ == '__main__':
    # This block provides a runnable example for testing and demonstration.
    # It fulfills the requirement for a self-testable module.

    def get_share_price(symbol: str) -> Optional[float]:
        """Test implementation of a share price provider."""
        prices = {
            "AAPL": 150.00,
            "TSLA": 300.00,
            "GOOGL": 2200.00,
        }
        # Simulate price changes for realism in testing
        if symbol == "AAPL":
            prices[symbol] += 10.50
        return prices.get(symbol.upper().strip())

    print("--- Running Backend Self-Test ---")
    my_account = None
    try:
        # --- US-001: Account Creation ---
        print("\n[US-001] Testing Account Creation...")
        my_account = Account(
            username='trader123',
            initial_deposit=10000.00,
            price_provider=get_share_price
        )
        print(f"Success: Account 'trader123' created with an initial deposit of ${my_account.cash_balance:,.2f}.")
        assert my_account.cash_balance == 10000.00
        assert len(my_account.transactions) == 1
        assert my_account.transactions[0]['type'] == 'DEPOSIT'

        try:
            Account(username='bad_user', initial_deposit=-100, price_provider=get_share_price)
        except ValueError as e:
            print(f"Success: Correctly caught invalid deposit: {e}")
            assert "positive number" in str(e)

        # --- US-002: Cash Management ---
        print("\n[US-002] Testing Cash Management...")
        new_balance = my_account.deposit(2000)
        print(f"Success: $2,000.00 deposited. New cash balance is ${new_balance:,.2f}.")
        assert new_balance == 12000.00
        new_balance = my_account.withdraw(1500)
        print(f"Success: $1,500.00 withdrawn. New cash balance is ${new_balance:,.2f}.")
        assert new_balance == 10500.00

        try:
            my_account.withdraw(99999)
        except InsufficientFundsError as e:
            print(f"Success: Correctly caught insufficient funds for withdrawal: {e}")
            assert "Insufficient funds" in str(e)

        # --- US-003: Trading ---
        print("\n[US-003] Testing Trading...")
        buy_res = my_account.buy_shares('AAPL', 10) # Price is 150 + 10.5 = 160.5
        total = buy_res['total_cost']
        price = buy_res['price_per_share']
        print(f"Success: Bought 10 shares of AAPL at ${price:,.2f} each for a total of ${total:,.2f}.")
        # Cash check: 10500.00 - 1605.00 = 8895.00
        assert abs(my_account.cash_balance - 8895.00) < 1e-9
        assert my_account.holdings['AAPL'] == 10

        sell_res = my_account.sell_shares('AAPL', 5)
        total = sell_res['total_proceeds']
        price = sell_res['price_per_share']
        print(f"Success: Sold 5 shares of AAPL at ${price:,.2f} each for a total of ${total:,.2f}.")
        # Cash check: 8895.00 + 802.50 = 9697.50
        assert abs(my_account.cash_balance - 9697.50) < 1e-9
        assert my_account.holdings['AAPL'] == 5

        try:
            my_account.sell_shares('GOOGL', 1)
        except InsufficientSharesError as e:
            print(f"Success: Correctly caught selling unowned shares: {e}")

        try:
            my_account.buy_shares('FAKE', 1)
        except InvalidSymbolError as e:
            print(f"Success: Correctly caught invalid symbol: {e}")

        # --- US-004: Reporting ---
        print("\n[US-004] Testing Reporting...")
        my_account.buy_shares('TSLA', 5) # 5 * 300 = 1500
        # Cash after TSLA buy: 9697.50 - 1500 = 8197.50
        assert abs(my_account.cash_balance - 8197.50) < 1e-9
        summary = my_account.get_portfolio_summary()
        
        # Net deposits = 10000 + 2000 - 1500 = 10500
        assert abs(summary['net_deposits'] - 10500.00) < 1e-9
        # Holdings Value = 2302.5
        assert abs(summary['total_shares_value'] - 2302.5) < 1e-9
        # Total Value = 10500.00
        assert abs(summary['total_portfolio_value'] - 10500.00) < 1e-9
        # P/L = 0.0
        assert abs(summary['profit_loss']) < 1e-9
        
        print(f"Portfolio Summary: {summary}")
        print(f"Final P/L: ${summary['profit_loss']:,.2f}")


        history = my_account.get_transaction_history()
        print("\n--- Transaction History (most recent first) ---")
        for tx in history:
            print(
                f"{tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {tx['type']:<10} "
                f"| Symbol: {tx.get('symbol', 'N/A'):<5} | Qty: {tx.get('quantity', 'N/A'):<4} "
                f"| Total: ${tx['total_amount']:>10,.2f}"
            )
        assert len(history) == 6
        assert history[0]['type'] == 'BUY' and history[0]['symbol'] == 'TSLA'

        print("\n--- Self-Test Complete ---")

    except (AccountError, ValueError) as e:
        print(f"\nAn unexpected error occurred during self-test: {e}")
        if my_account:
            print("Final state before error:")
            print(f"Cash: {my_account.cash_balance}")
            print(f"Holdings: {dict(my_account.holdings)}")
            print(f"Transactions: {len(my_account.transactions)}")
