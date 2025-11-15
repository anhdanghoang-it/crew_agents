import gradio as gr
import pandas as pd
from datetime import datetime
from typing import Optional

# Assuming 'accounts.py' is in the same directory and contains the Account class
# and custom exceptions as specified in the technical design.
from accounts import (
    Account,
    AccountError,
    InsufficientFundsError,
    InsufficientSharesError,
    InvalidSymbolError
)

# --- Pricing Provider ---
# As per the technical design, this function provides share prices.
# In a real app, this would call an API.
def get_share_price(symbol: str) -> Optional[float]:
    """
    Retrieves the current price for a given stock symbol.
    This is a mock implementation for the simulation.
    """
    prices = {
        "AAPL": 150.00,
        "TSLA": 300.00,
        "GOOGL": 2200.00,
    }
    return prices.get(symbol.upper())

# --- UI Helper Functions ---

def _format_success(message: str) -> str:
    """Formats a success message for Markdown display."""
    return f"<p style='color:green;'>{message}</p>"

def _format_error(message: str) -> str:
    """Formats an error message for Markdown display."""
    return f"<p style='color:red;'>{message}</p>"

# --- Gradio Event Handlers ---

def create_account(username, password, initial_deposit):
    """
    Handles the 'Create Account' button click.
    Creates a new Account object and transitions the UI to the dashboard view.
    """
    if not username or not password:
        return {
            creation_status: gr.update(value=_format_error("Error: Username and password are required.")),
        }
    try:
        # The password is not used in the backend as per the simple design,
        # but it's included in the UI for realism.
        account = Account(
            username=username,
            initial_deposit=float(initial_deposit),
            price_provider=get_share_price
        )
        
        # On successful creation, get initial portfolio state
        summary_updates = refresh_portfolio_components(account)
        history_updates = refresh_history_components(account)

        success_message = _format_success(
            f"Success: Account '{username}' created with an initial deposit of ${initial_deposit:,.2f}."
        )
        
        # This large dictionary updates all relevant components at once
        updates = {
            account_state: account,
            creation_view: gr.update(visible=False),
            dashboard_view: gr.update(visible=True),
            creation_status: gr.update(value=success_message),
        }
        updates.update(summary_updates)
        updates.update(history_updates)
        return updates

    except ValueError as e:
        # Catches "Initial deposit must be a positive number."
        return {
            creation_status: gr.update(value=_format_error(f"Error: {e}")),
            account_state: None,
            creation_view: gr.update(visible=True),
            dashboard_view: gr.update(visible=False),
        }

def refresh_portfolio_components(account: Optional[Account]):
    """
    Fetches portfolio summary and prepares updates for all portfolio UI components.
    """
    if not isinstance(account, Account):
        return {
            portfolio_value_txt: gr.update(value="N/A"),
            profit_loss_txt: gr.update(value="N/A"),
            cash_balance_txt: gr.update(value="N/A"),
            holdings_df: gr.update(value=pd.DataFrame(columns=["Symbol", "Quantity", "Current Price", "Total Value"])),
        }
        
    summary = account.get_portfolio_summary()
    
    # Create holdings dataframe with calculated values
    holdings_data = []
    for holding in summary['holdings']:
        symbol = holding['symbol']
        quantity = holding['quantity']
        price = get_share_price(symbol) or 0.0
        total_value = quantity * price
        holdings_data.append([symbol, quantity, f"${price:,.2f}", f"${total_value:,.2f}"])

    holdings_dataframe = pd.DataFrame(holdings_data, columns=["Symbol", "Quantity", "Current Price", "Total Value"])

    return {
        portfolio_value_txt: gr.update(value=f"${summary['total_portfolio_value']:,.2f}"),
        profit_loss_txt: gr.update(value=f"${summary['profit_loss']:,.2f}"),
        cash_balance_txt: gr.update(value=f"${summary['cash_balance']:,.2f}"),
        holdings_df: gr.update(value=holdings_dataframe),
        # Also update the cash balance display on the cash management tab
        cash_balance_display_cash_tab: gr.update(value=f"${summary['cash_balance']:,.2f}"),
    }

def refresh_history_components(account: Optional[Account]):
    """
    Fetches transaction history and prepares update for the history dataframe.
    """
    if not isinstance(account, Account):
        return {
            history_df: gr.update(value=pd.DataFrame(columns=["Timestamp", "Type", "Symbol", "Quantity", "Price", "Total"]))
        }

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
    
    return {history_df: gr.update(value=history_dataframe)}


def handle_cash_transaction(account: Account, amount: float, tx_type: str):
    """
    Handles both deposit and withdrawal actions.
    """
    if not isinstance(account, Account):
        return {cash_mgmt_status: gr.update(value=_format_error("Error: No active account."))}

    try:
        if amount <= 0:
            raise ValueError("Amount must be a positive number.")

        if tx_type == 'deposit':
            new_balance = account.deposit(amount)
            message = _format_success(f"Success: ${amount:,.2f} deposited. Your new cash balance is ${new_balance:,.2f}.")
        else: # withdraw
            new_balance = account.withdraw(amount)
            message = _format_success(f"Success: ${amount:,.2f} withdrawn. Your new cash balance is ${new_balance:,.2f}.")

        portfolio_updates = refresh_portfolio_components(account)
        updates = {
            account_state: account,
            cash_mgmt_status: gr.update(value=message),
        }
        updates.update(portfolio_updates)
        return updates

    except (ValueError, InsufficientFundsError) as e:
        return {cash_mgmt_status: gr.update(value=_format_error(f"Error: {e}"))}


def handle_trade(account: Account, action: str, symbol: str, quantity: int):
    """
    Handles the 'Execute Trade' button click for both BUY and SELL actions.
    """
    if not isinstance(account, Account):
        return {trade_status_box: gr.update(value=_format_error("Error: No active account."))}

    if not symbol or not quantity:
        return {trade_status_box: gr.update(value=_format_error("Error: Stock Symbol and Quantity are required."))}

    try:
        # Gradio Number input can be float, ensure it's an int for the backend
        quantity = int(quantity)

        if action == "BUY":
            result = account.buy_shares(symbol, quantity)
            msg = _format_success(
                f"Success: Bought {quantity} shares of {result['symbol']} at "
                f"${result['price_per_share']:,.2f} each for a total of ${result['total_cost']:,.2f}."
            )
        else:  # SELL
            result = account.sell_shares(symbol, quantity)
            msg = _format_success(
                f"Success: Sold {quantity} shares of {result['symbol']} at "
                f"${result['price_per_share']:,.2f} each for a total of ${result['total_proceeds']:,.2f}."
            )
        
        portfolio_updates = refresh_portfolio_components(account)
        history_updates = refresh_history_components(account)
        
        updates = {
            account_state: account,
            trade_status_box: gr.update(value=msg),
        }
        updates.update(portfolio_updates)
        updates.update(history_updates)
        return updates

    except (ValueError, InvalidSymbolError, InsufficientFundsError, InsufficientSharesError) as e:
        return {trade_status_box: gr.update(value=_format_error(str(e)))}
    except Exception as e:
        return {trade_status_box: gr.update(value=_format_error(f"An unexpected error occurred: {e}"))}


# --- Gradio UI Definition ---

with gr.Blocks(theme=gr.themes.Soft(), title="Trading Simulation Platform") as app:
    
    account_state = gr.State(None)
    
    gr.Markdown("# Trading Simulation Platform")
    gr.Markdown("A simple platform to simulate stock trading. Create an account to begin.")

    # --- 1. Account Creation View (Initially Visible) ---
    with gr.Column(elem_id="creation_view") as creation_view:
        with gr.Group():
            gr.Markdown("## Create a New Account")
            username_input = gr.Textbox(label="Username", placeholder="e.g., trader123")
            password_input = gr.Textbox(label="Password", type="password")
            deposit_input = gr.Number(label="Initial Deposit Amount ($)", value=10000.00, minimum=1.00)
            create_btn = gr.Button("Create Account", variant="primary")
            creation_status = gr.Markdown()

    # --- 2. Main Dashboard View (Initially Hidden) ---
    with gr.Tabs(elem_id="dashboard_view", visible=False) as dashboard_view:

        # --- Tab 1: Portfolio ---
        with gr.TabItem("Portfolio") as portfolio_tab:
            with gr.Row():
                with gr.Column(scale=3):
                    gr.Markdown("### Portfolio Summary")
                    portfolio_value_txt = gr.Textbox(label="Total Portfolio Value ($)", interactive=False)
                    profit_loss_txt = gr.Textbox(label="Total Profit / Loss ($)", interactive=False)
                    cash_balance_txt = gr.Textbox(label="Cash Balance ($)", interactive=False)
                with gr.Column(scale=1, min_width=150):
                    refresh_portfolio_btn = gr.Button("Refresh", variant="secondary")
            
            gr.Markdown("### Current Holdings")
            holdings_df = gr.Dataframe(
                headers=["Symbol", "Quantity", "Current Price", "Total Value"],
                datatype=["str", "number", "str", "str"],
                interactive=False
            )

        # --- Tab 2: Cash Management ---
        with gr.TabItem("Cash Management"):
            gr.Markdown("### Manage Your Cash Balance")
            cash_balance_display_cash_tab = gr.Textbox(label="Current Cash Balance", interactive=False)
            cash_mgmt_amount = gr.Number(label="Amount ($)", minimum=0.01)
            with gr.Row():
                deposit_btn = gr.Button("Deposit", variant="primary")
                withdraw_btn = gr.Button("Withdraw")
            cash_mgmt_status = gr.Markdown()
        
        # --- Tab 3: Trade ---
        with gr.TabItem("Trade"):
            gr.Markdown("### Execute a Trade")
            trade_action = gr.Dropdown(label="Action", choices=["BUY", "SELL"], value="BUY")
            trade_symbol = gr.Textbox(label="Stock Symbol", placeholder="e.g., AAPL, TSLA, GOOGL")
            trade_quantity = gr.Number(label="Quantity", minimum=1, precision=0, value=10)
            trade_btn = gr.Button("Execute Trade", variant="primary")
            trade_status_box = gr.Markdown()

        # --- Tab 4: History ---
        with gr.TabItem("History") as history_tab:
            gr.Markdown("### Transaction History")
            gr.Markdown("A log of all your account activities, sorted by most recent first.")
            history_df = gr.Dataframe(
                headers=["Timestamp", "Type", "Symbol", "Quantity", "Price", "Total"],
                datatype=["str", "str", "str", "str", "str", "str"],
                interactive=False,
                wrap=True
            )

    # --- Component lists for handler outputs ---
    portfolio_components = [portfolio_value_txt, profit_loss_txt, cash_balance_txt, holdings_df, cash_balance_display_cash_tab]
    history_components = [history_df]

    # --- Event Listener Wiring ---
    create_btn.click(
        fn=create_account,
        inputs=[username_input, password_input, deposit_input],
        outputs=[account_state, creation_view, dashboard_view, creation_status] + portfolio_components + history_components
    )
    
    refresh_portfolio_btn.click(
        fn=refresh_portfolio_components,
        inputs=[account_state],
        outputs=portfolio_components
    )

    deposit_btn.click(
        fn=lambda acc, amt: handle_cash_transaction(acc, amt, 'deposit'),
        inputs=[account_state, cash_mgmt_amount],
        outputs=[account_state, cash_mgmt_status] + portfolio_components
    )

    withdraw_btn.click(
        fn=lambda acc, amt: handle_cash_transaction(acc, amt, 'withdraw'),
        inputs=[account_state, cash_mgmt_amount],
        outputs=[account_state, cash_mgmt_status] + portfolio_components
    )

    trade_btn.click(
        fn=handle_trade,
        inputs=[account_state, trade_action, trade_symbol, trade_quantity],
        outputs=[account_state, trade_status_box] + portfolio_components + history_components
    )
    
    history_tab.select(
        fn=refresh_history_components,
        inputs=[account_state],
        outputs=history_components
    )

if __name__ == "__main__":
    app.launch()