import gradio as gr
from typing import Optional, Dict
import pandas as pd
from datetime import datetime

# Assuming 'accounts.py' is in the same directory and contains the Account class
# and its custom exceptions as specified in the design document.
from accounts import (
    Account,
    AccountError,
    InsufficientFundsError,
    InsufficientSharesError,
    InvalidSymbolError,
)

# --- Pricing Provider (as specified in technical design) ---
def get_share_price(symbol: str) -> Optional[float]:
    """
    Retrieves the current price for a given stock symbol.
    This is a test implementation. In a real application, this would
    call an external market data API.
    """
    prices = {
        "AAPL": 150.00,
        "TSLA": 300.00,
        "GOOGL": 2200.00,
    }
    return prices.get(symbol.upper().strip())


# --- UI Helper Functions ---

def format_currency(value: float) -> str:
    """Formats a float into a currency string, e.g., $1,234.56 or -$2,000.00"""
    if value is None:
        return "$0.00"
    if value < 0:
        return f"-${abs(value):,.2f}"
    return f"${value:,.2f}"

def refresh_portfolio_view(account: Optional[Account]) -> Dict:
    """
    Generates a dictionary of Gradio updates for all portfolio and cash balance components.
    This is a central function to keep the UI consistent after any transaction.
    """
    if not isinstance(account, Account):
        # Return updates to clear/reset the fields if no account is active
        return {
            p_total_value: gr.update(value=""),
            p_profit_loss: gr.update(value=""),
            p_cash_balance: gr.update(value=""),
            cm_cash_balance: gr.update(value=""),
            p_holdings_df: gr.update(value=None),
        }

    summary = account.get_portfolio_summary()

    # Prepare holdings DataFrame
    holdings_data = []
    if summary['holdings']:
        for holding in summary['holdings']:
            symbol = holding['symbol']
            quantity = holding['quantity']
            price = get_share_price(symbol) or 0.0
            total_value = quantity * price
            holdings_data.append([symbol, quantity, format_currency(price), format_currency(total_value)])
    
    holdings_df = pd.DataFrame(
        holdings_data,
        columns=["Symbol", "Quantity", "Current Price", "Total Value"]
    ) if holdings_data else None

    # Return a dictionary of updates
    return {
        p_total_value: gr.update(value=format_currency(summary['total_portfolio_value'])),
        p_profit_loss: gr.update(value=format_currency(summary['profit_loss'])),
        p_cash_balance: gr.update(value=format_currency(summary['cash_balance'])),
        cm_cash_balance: gr.update(value=format_currency(summary['cash_balance'])),
        p_holdings_df: gr.update(value=holdings_df),
    }

def refresh_history_view(account: Optional[Account]) -> gr.update:
    """Generates a Gradio update for the transaction history DataFrame."""
    if not isinstance(account, Account):
        return gr.update(value=None)

    history = account.get_transaction_history()
    history_data = []
    for tx in history:
        symbol_val = tx.get('symbol', 'N/A')
        quantity_val = tx.get('quantity', 'N/A')
        price_per_share = tx.get('price_per_share')

        history_data.append([
            tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            tx['type'],
            symbol_val,
            quantity_val,
            format_currency(price_per_share) if price_per_share is not None else 'N/A',
            format_currency(tx['total_amount'])
        ])
    
    history_df = pd.DataFrame(
        history_data,
        columns=["Timestamp", "Type", "Symbol", "Quantity", "Price", "Total"]
    ) if history_data else None

    return gr.update(value=history_df)


# --- Event Handler Functions ---

def handle_create_account(username, password, initial_deposit):
    """Event handler for the 'Create Account' button."""
    if not username or not password:
        return {
            create_status_box: gr.update(value="Error: Username and password are required.")
        }
    
    try:
        account = Account(
            username=username,
            initial_deposit=float(initial_deposit),
            price_provider=get_share_price
        )
        
        success_msg = f"Success: Account '{username}' created with an initial deposit of {format_currency(initial_deposit)}."
        
        # On success, hide creation view, show dashboard, and populate data
        initial_updates = refresh_portfolio_view(account)
        initial_updates.update({
            account_state: account,
            creation_view: gr.update(visible=False),
            dashboard_view: gr.update(visible=True),
            create_status_box: gr.update(value=success_msg),
        })
        return initial_updates

    except ValueError as e:
        # Handles "Initial deposit must be a positive number." from backend
        return {create_status_box: gr.update(value=f"Error: {e}")}
    except Exception as e:
        return {create_status_box: gr.update(value=f"An unexpected error occurred: {e}")}


def handle_deposit(account: Account, amount: float):
    """Event handler for the 'Deposit' button."""
    if not isinstance(account, Account):
        return {cm_status_box: gr.update(value="Error: No active account.")}
    if not amount or amount <= 0:
        return {cm_status_box: gr.update(value="Error: Amount must be a positive number.")}
        
    try:
        new_balance = account.deposit(float(amount))
        msg = f"Success: {format_currency(amount)} deposited. Your new cash balance is {format_currency(new_balance)}."
        
        updates = refresh_portfolio_view(account)
        updates.update({
            account_state: account,
            cm_status_box: gr.update(value=msg),
        })
        return updates

    except (ValueError, AccountError) as e:
        return {cm_status_box: gr.update(value=f"Error: {e}")}


def handle_withdraw(account: Account, amount: float):
    """Event handler for the 'Withdraw' button."""
    if not isinstance(account, Account):
        return {cm_status_box: gr.update(value="Error: No active account.")}
    if not amount or amount <= 0:
        return {cm_status_box: gr.update(value="Error: Amount must be a positive number.")}

    try:
        new_balance = account.withdraw(float(amount))
        msg = f"Success: {format_currency(amount)} withdrawn. Your new cash balance is {format_currency(new_balance)}."
        
        updates = refresh_portfolio_view(account)
        updates.update({
            account_state: account,
            cm_status_box: gr.update(value=msg),
        })
        return updates

    except (ValueError, InsufficientFundsError) as e:
        return {cm_status_box: gr.update(value=f"Error: {e}")}


def handle_trade(account: Account, action: str, symbol: str, quantity: int):
    """Event handler for the 'Execute Trade' button."""
    if not isinstance(account, Account):
        return {trade_status_box: gr.update(value="Error: No active account.")}
    if not (symbol and quantity and quantity > 0):
        return {trade_status_box: gr.update(value="Error: Stock Symbol and a positive Quantity are required.")}

    try:
        msg = ""
        quantity = int(quantity) # Ensure integer conversion

        if action == "BUY":
            result = account.buy_shares(symbol, quantity)
            msg = f"Success: Bought {quantity} shares of {result['symbol']} at {format_currency(result['price_per_share'])} each for a total of {format_currency(result['total_cost'])}."
        else: # SELL
            result = account.sell_shares(symbol, quantity)
            msg = f"Success: Sold {quantity} shares of {result['symbol']} at {format_currency(result['price_per_share'])} each for a total of {format_currency(result['total_proceeds'])}."

        updates = refresh_portfolio_view(account)
        updates.update({
            account_state: account,
            trade_status_box: gr.update(value=msg)
        })
        return updates

    except (ValueError, InvalidSymbolError, InsufficientFundsError, InsufficientSharesError) as e:
        return {trade_status_box: gr.update(value=f"Error: {e}")}
    except Exception as e:
        return {trade_status_box: gr.update(value=f"An unexpected error occurred: {e}")}


# --- Gradio UI Definition ---

with gr.Blocks(title="Trading Simulation Platform", theme=gr.themes.Soft()) as app:
    gr.Markdown("# Trading Simulation Platform")
    gr.Markdown("Create an account to start managing your virtual portfolio. Deposit funds, trade stocks, and track your performance.")
    
    # State object to hold the backend Account instance for the session
    account_state = gr.State(value=None)

    # --- View 1: Account Creation (Visible by default) ---
    with gr.Group(visible=True) as creation_view:
        with gr.Row():
            create_username = gr.Textbox(label="Username", placeholder="e.g., trader123")
            create_password = gr.Textbox(label="Password", type="password")
            create_deposit = gr.Number(label="Initial Deposit Amount ($)", value=10000.00, minimum=0.01)
        
        create_button = gr.Button("Create Account", variant="primary")
        create_status_box = gr.Textbox(label="Status", interactive=False)

    # --- View 2: Main Dashboard (Initially hidden) ---
    with gr.Tabs(visible=False) as dashboard_view:
        # --- Tab 1: Portfolio ---
        with gr.TabItem("Portfolio") as portfolio_tab:
            with gr.Row():
                p_total_value = gr.Textbox(label="Total Portfolio Value ($)", interactive=False)
                p_profit_loss = gr.Textbox(label="Total Profit / Loss ($)", interactive=False)
                p_cash_balance = gr.Textbox(label="Cash Balance ($)", interactive=False)
            
            p_refresh_button = gr.Button("Refresh")
            gr.Markdown("### Current Holdings")
            p_holdings_df = gr.Dataframe(
                headers=["Symbol", "Quantity", "Current Price", "Total Value"],
                datatype=["str", "number", "str", "str"],
                interactive=False
            )

        # --- Tab 2: Cash Management ---
        with gr.TabItem("Cash Management") as cash_management_tab:
            cm_cash_balance = gr.Textbox(label="Current Cash Balance", interactive=False)
            cm_amount_num = gr.Number(label="Amount ($)", minimum=0.01, info="Enter the amount to deposit or withdraw.")
            with gr.Row():
                cm_deposit_button = gr.Button("Deposit")
                cm_withdraw_button = gr.Button("Withdraw")
            cm_status_box = gr.Textbox(label="Status", interactive=False)

        # --- Tab 3: Trade ---
        with gr.TabItem("Trade") as trade_tab:
            with gr.Row():
                trade_action = gr.Dropdown(label="Action", choices=["BUY", "SELL"], value="BUY")
                trade_symbol = gr.Textbox(label="Stock Symbol", placeholder="e.g., AAPL, TSLA, GOOGL")
                trade_quantity = gr.Number(label="Quantity", minimum=1, precision=0, info="Must be a whole number.")
            
            trade_button = gr.Button("Execute Trade", variant="primary")
            trade_status_box = gr.Textbox(label="Status", interactive=False)
            gr.Examples(
                examples=[
                    ["BUY", "AAPL", 10],
                    ["SELL", "TSLA", 5],
                ],
                inputs=[trade_action, trade_symbol, trade_quantity]
            )

        # --- Tab 4: History ---
        with gr.TabItem("History") as history_tab:
            h_history_df = gr.Dataframe(
                headers=["Timestamp", "Type", "Symbol", "Quantity", "Price", "Total"],
                datatype=["str", "str", "str", "str", "str", "str"],
                interactive=False,
                label="Transaction History"
            )

    # --- Event Listeners Wiring ---

    # List of components updated after a successful account creation (which triggers portfolio/history refresh)
    portfolio_outputs = [p_total_value, p_profit_loss, p_cash_balance, cm_cash_balance, p_holdings_df]
    history_outputs = [h_history_df]
    
    # 1. Account Creation (Updates portfolio and history on success)
    create_button.click(
        fn=handle_create_account,
        inputs=[create_username, create_password, create_deposit],
        outputs=[
            account_state,
            creation_view,
            dashboard_view,
            create_status_box,
        ] + portfolio_outputs
    ).then(
        fn=refresh_history_view,
        inputs=[account_state],
        outputs=history_outputs
    )

    # 2. Portfolio Refresh
    p_refresh_button.click(
        fn=refresh_portfolio_view,
        inputs=[account_state],
        outputs=portfolio_outputs
    )

    # 3. Tab Select triggers refresh
    portfolio_tab.select(
        fn=refresh_portfolio_view,
        inputs=[account_state],
        outputs=portfolio_outputs
    )

    # 4. Cash Management
    deposit_flow_outputs = [account_state, cm_status_box] + portfolio_outputs
    cm_deposit_button.click(
        fn=handle_deposit,
        inputs=[account_state, cm_amount_num],
        outputs=deposit_flow_outputs
    ).then(
        fn=refresh_history_view,
        inputs=[account_state],
        outputs=history_outputs
    )
    
    withdraw_flow_outputs = [account_state, cm_status_box] + portfolio_outputs
    cm_withdraw_button.click(
        fn=handle_withdraw,
        inputs=[account_state, cm_amount_num],
        outputs=withdraw_flow_outputs
    ).then(
        fn=refresh_history_view,
        inputs=[account_state],
        outputs=history_outputs
    )

    # 5. Trading
    trade_flow_outputs = [account_state, trade_status_box] + portfolio_outputs
    trade_button.click(
        fn=handle_trade,
        inputs=[account_state, trade_action, trade_symbol, trade_quantity],
        outputs=trade_flow_outputs
    ).then(
        fn=refresh_history_view,
        inputs=[account_state],
        outputs=history_outputs
    )

    # 6. History Tab Select
    history_tab.select(
        fn=refresh_history_view,
        inputs=[account_state],
        outputs=history_outputs
    )

if __name__ == "__main__":
    app.launch()