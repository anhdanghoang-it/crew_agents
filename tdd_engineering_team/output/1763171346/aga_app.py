```python
import gradio as gr
from accounts import Account, InsufficientFundsError, InsufficientSharesError, InvalidSymbolError
from typing import Optional, Dict
import pandas as pd

# --- Share Pricing Provider (from technical_design_task) ---
def get_share_price(symbol: str) -> Optional[float]:
    """
    Retrieves the current price for a given stock symbol.
    This is a mock implementation as specified in the technical design. In a real
    application, this would call an external market data API.

    Args:
        symbol: The stock symbol (e.g., 'AAPL').

    Returns:
        The price as a float, or None if the symbol is not found.
    """
    prices = {
        "AAPL": 150.00,
        "TSLA": 300.00,
        "GOOGL": 2200.00,
    }
    # Normalize symbol for case-insensitive and whitespace-robust lookup
    return prices.get(symbol.upper().strip())

# --- UI Event Handlers ---

def handle_create_account(username: str, password: str, deposit: float, usernames: set) -> Dict:
    """
    Handles the 'Create Account' button click event. Validates input, creates
    an Account object, and transitions the UI to the main dashboard.

    Returns:
        A dictionary of Gradio updates for multiple components.
    """
    if not username or not password:
        return {create_status_box: gr.update(value="Error: Username and password cannot be empty.")}
    
    # Per US-001 AC-2, check for username uniqueness at the UI layer.
    if username in usernames:
        return {create_status_box: gr.update(value=f"Error: Username '{username}' is already taken. Please choose a different username.")}
    
    try:
        account = Account(username, deposit, get_share_price)
        usernames.add(username)
        # Message from US-001 AC-1
        success_msg = f"Success: Account '{username}' created with an initial deposit of ${deposit:,.2f}."
        
        # On successful creation, immediately fetch portfolio info to populate the dashboard.
        summary = account.get_portfolio_summary()
        holdings_data = [] # empty initially
        
        # Return a dictionary of updates for a seamless UI transition.
        return {
            account_state: account,
            usernames_state: usernames,
            creation_view: gr.update(visible=False),
            dashboard_view: gr.update(visible=True),
            create_status_box: gr.update(value=success_msg),
            # Update portfolio tab
            portfolio_total_value: f"${summary['total_portfolio_value']:,.2f}",
            portfolio_pl: f"${summary['profit_loss']:,.2f}",
            portfolio_cash_balance: f"${summary['cash_balance']:,.2f}",
            # Update cash management tab
            cash_balance_display: f"${summary['cash_balance']:,.2f}",
            holdings_df: pd.DataFrame(holdings_data, columns=["Symbol", "Quantity", "Current Price", "Total Value"]),
        }

    except ValueError as e:
        # Catches error from Account constructor (e.g., invalid deposit from US-001 AC-3)
        return {create_status_box: gr.update(value=f"Error: {e}")}

def refresh_portfolio_view(account: Account) -> Dict:
    """
    Refreshes all components on the Portfolio tab and the cash balance display
    on the Cash Management tab with the latest data from the Account object.
    """
    if not isinstance(account, Account):
        # Handle case where function is called before an account is created.
        return {
            portfolio_total_value: "", portfolio_pl: "", portfolio_cash_balance: "",
            holdings_df: pd.DataFrame([], columns=["Symbol", "Quantity", "Current Price", "Total Value"]),
            cash_balance_display: ""
        }

    summary = account.get_portfolio_summary()
    
    holdings_data = []
    for h in summary['holdings']:
        symbol = h['symbol']
        quantity = h['quantity']
        price = get_share_price(symbol)
        value = (quantity * price) if price is not None else 0
        holdings_data.append([symbol, quantity, f"${price:,.2f}" if price is not None else "N/A", f"${value:,.2f}"])
    
    holdings_dataframe = pd.DataFrame(holdings_data, columns=["Symbol", "Quantity", "Current Price", "Total Value"])

    return {
        portfolio_total_value: f"${summary['total_portfolio_value']:,.2f}",
        portfolio_pl: f"${summary['profit_loss']:,.2f}",
        portfolio_cash_balance: f"${summary['cash_balance']:,.2f}",
        holdings_df: holdings_dataframe,
        cash_balance_display: f"${summary['cash_balance']:,.2f}", # Keep cash mgmt tab sync'd
    }

def refresh_history_view(account: Account) -> Dict:
    """Refreshes the transaction history dataframe."""
    if not isinstance(account, Account):
        return {history_df: pd.DataFrame([], columns=["Timestamp", "Type", "Symbol", "Quantity", "Price", "Total"])}
    
    history = account.get_transaction_history()
    history_data = [
        [
            tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            tx['type'],
            tx['symbol'] or 'N/A',
            tx['quantity'] or 'N/A',
            f"${tx['price_per_share']:,.2f}" if tx['price_per_share'] is not None else 'N/A',
            f"${tx['total_amount']:,.2f}"
        ] for tx in history
    ]
    history_dataframe = pd.DataFrame(history_data, columns=["Timestamp", "Type", "Symbol", "Quantity", "Price", "Total"])
    return {history_df: history_dataframe}

def handle_deposit(account: Account, amount: float) -> Dict:
    """Handles the 'Deposit' button click event."""
    if not isinstance(account, Account):
        return {cash_mgmt_status_box: "Error: No active account."}
    
    try:
        new_balance = account.deposit(amount)
        # Message from US-002 AC-1
        success_msg = f"Success: ${amount:,.2f} deposited. Your new cash balance is ${new_balance:,.2f}."
        
        updates = refresh_portfolio_view(account)
        updates[cash_mgmt_status_box] = success_msg
        updates[account_state] = account
        return updates

    except ValueError as e: # From US-002 AC-4
        return {cash_mgmt_status_box: f"Error: {e}"}

def handle_withdraw(account: Account, amount: float) -> Dict:
    """Handles the 'Withdraw' button click event."""
    if not isinstance(account, Account):
        return {cash_mgmt_status_box: "Error: No active account."}

    try:
        new_balance = account.withdraw(amount)
        # Message from US-002 AC-2
        success_msg = f"Success: ${amount:,.2f} withdrawn. Your new cash balance is ${new_balance:,.2f}."
        
        updates = refresh_portfolio_view(account)
        updates[cash_mgmt_status_box] = success_msg
        updates[account_state] = account
        return updates

    except (ValueError, InsufficientFundsError) as e: # From US-002 AC-3 & AC-4
        return {cash_mgmt_status_box: f"Error: {e}"}

def handle_trade(account: Account, action: str, symbol: str, quantity: int) -> Dict:
    """Handles the 'Execute Trade' button click event."""
    if not isinstance(account, Account):
        return {trade_status_box: "Error: No active account."}
    if not (symbol and quantity):
        return {trade_status_box: "Error: Symbol and quantity are required."}
    
    try:
        quantity_int = int(quantity)
        
        if action == "BUY":
            result = account.buy_shares(symbol, quantity_int)
            # Message from US-003 AC-1
            msg = (f"Success: Bought {result['quantity']} shares of {result['symbol']} "
                   f"at ${result['price_per_share']:,.2f} each for a total of ${result['total_cost']:,.2f}.")
        else: # SELL
            result = account.sell_shares(symbol, quantity_int)
            # Message from US-003 AC-2
            msg = (f"Success: Sold {result['quantity']} shares of {result['symbol']} "
                   f"at ${result['price_per_share']:,.2f} each for a total of ${result['total_proceeds']:,.2f}.")

        updates = refresh_portfolio_view(account)
        updates[trade_status_box] = msg
        updates[account_state] = account
        return updates

    except (InsufficientFundsError, InsufficientSharesError, InvalidSymbolError, ValueError) as e:
        # Catches all specific, user-facing errors from the backend (US-003 AC-3,4,5,6)
        return {trade_status_box: gr.update(value=f"Error: {e}")}
    except Exception as e:
        return {trade_status_box: gr.update(value=f"An unexpected system error occurred: {e}")}


# --- Gradio UI Definition ---

with gr.Blocks(theme=gr.themes.Soft(), title="Trading Simulation Platform") as app:
    # State management for the user session
    account_state = gr.State(None)
    usernames_state = gr.State(set()) # UI-layer state to track created usernames

    gr.Markdown("# Trading Simulation Platform")
    gr.Markdown("Create a new account to start trading, or use the tabs to manage your portfolio.")

    # --- 1. Account Creation View (visible by default) ---
    with gr.Column(visible=True) as creation_view:
        with gr.Accordion("Create New Account", open=True):
            create_username = gr.Textbox(label="Username", placeholder="e.g., trader123")
            create_password = gr.Textbox(label="Password", type="password", placeholder="Enter a secure password")
            create_deposit = gr.Number(label="Initial Deposit Amount ($)", value=10000.00, minimum=0.01)
            create_button = gr.Button("Create Account", variant="primary")
            create_status_box = gr.Textbox(label="Status", interactive=False)
            gr.Examples(
                examples=[
                    ["trader_jane", "password123", 15000],
                    ["new_user", "secure_pass", 5000],
                ],
                inputs=[create_username, create_password, create_deposit]
            )

    # --- 2. Main Dashboard View (initially hidden) ---
    with gr.Tabs(visible=False) as dashboard_view:
        
        with gr.TabItem("Portfolio", id=0) as portfolio_tab:
            with gr.Row():
                portfolio_refresh_button = gr.Button("Refresh")
            with gr.Row():
                portfolio_total_value = gr.Textbox(label="Total Portfolio Value ($)", interactive=False)
                portfolio_pl = gr.Textbox(label="Total Profit / Loss ($)", interactive=False)
                portfolio_cash_balance = gr.Textbox(label="Cash Balance ($)", interactive=False)
            holdings_df = gr.Dataframe(
                label="Current Holdings",
                headers=["Symbol", "Quantity", "Current Price", "Total Value"],
                datatype=["str", "number", "str", "str"],
                interactive=False,
                col_count=(4, "fixed")
            )

        with gr.TabItem("Cash Management", id=1) as cash_mgmt_tab:
            cash_balance_display = gr.Textbox(label="Current Cash Balance", interactive=False)
            cash_mgmt_amount = gr.Number(label="Amount ($)", minimum=0.01)
            with gr.Row():
                deposit_button = gr.Button("Deposit")
                withdraw_button = gr.Button("Withdraw")
            cash_mgmt_status_box = gr.Textbox(label="Status", interactive=False)

        with gr.TabItem("Trade", id=2) as trade_tab:
            trade_action = gr.Dropdown(label="Action", choices=["BUY", "SELL"], value="BUY")
            trade_symbol = gr.Textbox(label="Stock Symbol (e.g., AAPL)", placeholder="AAPL")
            trade_quantity = gr.Number(label="Quantity", minimum=1, precision=0, value=1)
            trade_button = gr.Button("Execute Trade", variant="primary")
            trade_status_box = gr.Textbox(label="Status", interactive=False)
            gr.Examples(
                examples=[["BUY", "AAPL", 10], ["SELL", "TSLA", 5], ["BUY", "GOOGL", 2]],
                inputs=[trade_action, trade_symbol, trade_quantity]
            )

        with gr.TabItem("History", id=3) as history_tab:
            history_df = gr.Dataframe(
                label="Transaction History",
                headers=["Timestamp", "Type", "Symbol", "Quantity", "Price", "Total"],
                datatype=["str", "str", "str", "str", "str", "str"],
                interactive=False,
                col_count=(6, "fixed"),
                wrap=True
            )

    # --- Event Handlers Wiring ---
    
    # Define a list of all components that need updating after a financial transaction.
    portfolio_outputs = [
        portfolio_total_value, portfolio_pl, portfolio_cash_balance,
        holdings_df, cash_balance_display
    ]

    # 1. Account Creation
    create_button.click(
        fn=handle_create_account,
        inputs=[create_username, create_password, create_deposit, usernames_state],
        outputs=[account_state, usernames_state, creation_view, dashboard_view, create_status_box] + portfolio_outputs
    )

    # 2. Portfolio View Refresh (Button and Tab Select)
    portfolio_refresh_button.click(fn=refresh_portfolio_view, inputs=[account_state], outputs=portfolio_outputs)
    portfolio_tab.select(fn=refresh_portfolio_view, inputs=[account_state], outputs=portfolio_outputs)

    # 3. Cash Management
    deposit_button.click(
        fn=handle_deposit,
        inputs=[account_state, cash_mgmt_amount],
        outputs=[cash_mgmt_status_box, account_state] + portfolio_outputs
    )
    withdraw_button.click(
        fn=handle_withdraw,
        inputs=[account_state, cash_mgmt_amount],
        outputs=[cash_mgmt_status_box, account_state] + portfolio_outputs
    )
    cash_mgmt_tab.select(fn=refresh_portfolio_view, inputs=[account_state], outputs=portfolio_outputs)

    # 4. Trading
    trade_button.click(
        fn=handle_trade,
        inputs=[account_state, trade_action, trade_symbol, trade_quantity],
        outputs=[trade_status_box, account_state] + portfolio_outputs
    )

    # 5. History View
    history_tab.select(fn=refresh_history_view, inputs=[account_state], outputs=[history_df])


if __name__ == "__main__":
    app.launch()
```