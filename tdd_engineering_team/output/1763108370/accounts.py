class InvalidDepositAmount(Exception):
    pass

class InsufficientFunds(Exception):
    pass

class InvalidQuantity(Exception):
    pass

class Account:
    def __init__(self, username: str, email: str, password: str):
        """
        Initializes a new account.

        Args:
            username (str): The username of the account holder.
            email (str): The email address of the account holder.
            password (str): The password for the account.
        """
        self.username = username
        self.email = email
        self.password = self._hash_password(password)
        self.balance = 0.0
        self.holdings = {}
        self.transactions = []
        self.initial_deposit = 0.0

    def _hash_password(self, password: str) -> str:
        """
        Hashes the provided password.

        Args:
            password (str): Plaintext password.

        Returns:
            str: Hashed password.
        """
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def deposit_funds(self, amount: float) -> dict:
        """
        Deposits funds into the account.

        Args:
            amount (float): The amount to deposit (must be greater than 0).

        Returns:
            dict: {
                "success": bool,
                "message": str
            }
        """
        if amount <= 0:
            raise InvalidDepositAmount("Deposit amount must be greater than $0.")

        self.balance += amount
        self.initial_deposit += amount
        self.transactions.append({"type": "Deposit", "amount": amount})
        return {"success": True, "message": "Funds successfully deposited!"}

    def buy_shares(self, symbol: str, quantity: int, get_share_price: callable) -> dict:
        """
        Buys shares for the user, reducing account balance accordingly.

        Args:
            symbol (str): Stock symbol (e.g., "AAPL").
            quantity (int): Number of shares to buy.
            get_share_price (callable): Function to fetch the stock's current price.

        Returns:
            dict: {
                "success": bool,
                "message": str
            }
        """
        if quantity <= 0:
            raise InvalidQuantity("Quantity must be greater than 0.")

        price = get_share_price(symbol)
        total_cost = price * quantity

        if self.balance < total_cost:
            raise InsufficientFunds("Insufficient funds to make this purchase.")

        self.balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self.transactions.append({
            "type": "Buy",
            "symbol": symbol,
            "quantity": quantity,
            "price_per_share": price,
            "total_cost": total_cost
        })
        return {"success": True, "message": "Shares successfully purchased!"}

# Function to simulate retrieving share price
def get_share_price(symbol: str) -> float:
    """Returns a fixed share price for testing."""
    stock_prices = {"AAPL": 150.0, "TSLA": 250.0, "GOOGL": 2800.0}
    return stock_prices.get(symbol, 0)