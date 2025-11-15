```python
import gradio as gr
import pandas as pd
from datetime import datetime

# Assuming 'accounts.py' and 'pricing.py' are in the same directory.
# This app.py file integrates with them as per the technical design.
from accounts import Account, AccountError, InsufficientFundsError, InsufficientSharesError, InvalidSymbolError
from pricing import get_share_price

# --- UI Helper Functions ---

def format_currency(amount):
    """Formats a float as a currency string, handling negative values."""
    if amount is None:
        return "$0.00"
    return f"${amount:,.2f}" if amount >= 0 else f"-${abs(amount):,.2f}"

# --- Gradio Handler Functions ---

def handle_create_account(username, password, initial_deposit):
    """
    Handles the 'Create Account' button click.
    Corresponds to US-001.
    """
    if not username or not password:
        return {
            creation_status_box: gr.update(value="Error: Username and Password are required."),
            account_state: None,
            creation_view: gr.update(visible=True),
            main_dashboard: gr.update(visible=False),
        }
    
    try:
        # Per the design, the Account class handles deposit validation.
        account = Account(
            username=username,
            initial_deposit=float(initial_deposit),
            price_provider=get_share_price
        )
        success_message = f"Success: Account '{username}' created with an initial deposit of {format_currency(initial_deposit)}."
        return {
            creation_status_box: gr.update(value=success_message),
            account_state: account,
            creation_view: gr.update(visible=False),
            main_dashboard: gr.update(visible=True),
        }
    except ValueError as e:
        # Catches invalid deposit from Account constructor.
        return {
            creation_status_box: gr.update(value=f"Error: {e}"),
            account_state: None,
            creation_view: gr.update(visible=True),
            main_dashboard: gr.update(visible=False),
        }

def refresh_portfolio_view(account: Account):
    """
    Refreshes all components on the Portfolio tab.
    Corresponds to US-004.
    """
    if not isinstance(account, Account):
        return {
            portfolio_value_tb: "",
            portfolio_pl_tb: "",
            portfolio_cash_tb: "",
            cash_management_balance_tb: "",
            holdings_df: pd.DataFrame(columns=["Symbol", "Quantity", "Current Price", "Total Value"])
        }
    
    summary = account.get_portfolio_summary()
    
    holdings_data = [
        [
            h['symbol'],
            h['quantity'],
            format_currency(h['price']),
            format_currency(h['value'])
        ] for h in summary['holdings_with_prices']
    ]
    
    holdings_df_data = pd.DataFrame(
        holdings_data,
        columns=["Symbol", "Quantity", "Current Price", "Total Value"]
    )
    
    return {
        portfolio_value_tb: format_currency(summary['total_portfolio_value']),
        portfolio_pl_tb: format_currency(summary['profit_loss']),
        portfolio_cash_tb: format_currency(summary['cash_balance']),
        cash_management_balance_tb: format_currency(summary['cash_balance']),
        holdings_df: holdings_df_data
    }

def refresh_history_view(account: Account):
    """
    Refreshes the transaction history dataframe.
    Corresponds to US-004.
    """
    if not isinstance(account, Account):
        return gr.update(value=pd.DataFrame(columns=["Timestamp", "Type", "Symbol", "Quantity", "Price", "Total"]))
        
    history = account.get_transaction_history()
    history_data = [
        [
            tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            tx['type'],
            tx['symbol'] or 'N/A',
            tx['quantity'] or 'N/A',
            format_currency(tx['price_per_share']) if tx['price_per_share'] is not None else 'N/A',
            format_currency(tx['total_amount'])
        ] for tx in history
    ]
    
    history_df = pd.DataFrame(
        history_data,
        columns=["Timestamp", "Type", "Symbol", "Quantity", "Price", "Total"]
    )
    return gr.update(value=history_df)

def handle_deposit(account: Account, amount: float):
    """
    Handles cash deposit.
    Corresponds to US-002.
    """
    if not isinstance(account, Account):
        return {cash_management_status_box: "Error: No active account.", account_state: account}
    if not amount or amount <= 0:
        return {cash_management_status_box: "Error: Amount must be a positive number.", account_state: account}

    try:
        new_balance = account.deposit(amount)
        message = f"Success: {format_currency(amount)} deposited. Your new cash balance is {format_currency(new_balance)}."
        return {
            cash_management_status_box: message,
            account_state: account
        }
    except (ValueError, AccountError) as e:
        return {
            cash_management_status_box: f"Error: {e}",
            account_state: account
        }

def handle_withdraw(account: Account, amount: float):
    """
    Handles cash withdrawal.
    Corresponds to US-002.
    """
    if not isinstance(account, Account):
        return {cash_management_status_box: "Error: No active account.", account_state: account}
    if not amount or amount <= 0:
        return {cash_management_status_box: "Error: Amount must be a positive number.", account_state: account}
        
    try:
        new_balance = account.withdraw(amount)
        message = f"Success: {format_currency(amount)} withdrawn. Your new cash balance is {format_currency(new_balance)}."
        return {
            cash_management_status_box: message,
            account_state: account
        }
    except (ValueError, InsufficientFundsError) as e:
        return {
            cash_management_status_box: f"Error: {e}",
            account_state: account
        }

def handle_trade(account: Account, action: str, symbol: str, quantity: int):
    """
    Handles share buying and selling.
    Corresponds to US-003.
    """
    if not isinstance(account, Account):
        return {trade_status_box: "Error: No active account.", account_state: account}
    if not symbol or not quantity:
        return {trade_status_box: "Error: Stock Symbol and Quantity are required.", account_state: account}
    
    try:
        # Gradio Number component with precision=0 already ensures integer
        quantity = int(quantity)
        message = ""
        if action == "BUY":
            result = account.buy_shares(symbol, quantity)
            message = (f"Success: Bought {quantity} shares of {result['symbol']} at "
                       f"{format_currency(result['price_per_share'])} each for a total of {format_currency(result['total_cost'])}.")
        else:  # SELL
            result = account.sell_shares(symbol, quantity)
            message = (f"Success: Sold {quantity} shares of {result['symbol']} at "
                       f"{format_currency(result['price_per_share'])} each for a total of {format_currency(result['total_proceeds'])}.")
        
        return {
            trade_status_box: message,
            account_state: account
        }
    except (ValueError, InvalidSymbolError, InsufficientFundsError, InsufficientSharesError) as e:
        return {
            trade_status_box: f"Error: {e}",
            account_state: account
        }

# --- Gradio UI Layout ---

with gr.Blocks(title="Trading Simulation Platform", theme=gr.themes.Soft()) as app:
    gr.Markdown("# Trading Simulation Platform")
    gr.Markdown("Create a virtual account, manage cash, and trade stocks to track your portfolio performance.")

    # State object to hold the user's Account instance across the session
    account_state = gr.State(None)

    # Stage 1: Account Creation View
    with gr.Group(visible=True) as creation_view:
        with gr.Row():
            gr.Markdown("## Create Your Account")
        with gr.Row():
            create_username_tb = gr.Textbox(label="Username", placeholder="e.g., trader123")
            create_password_tb = gr.Textbox(label="Password", type="password")
        create_deposit_num = gr.Number(label="Initial Deposit Amount ($)", value=10000.00, minimum=0.01)
        create_account_btn = gr.Button("Create Account", variant="primary")
        creation_status_box = gr.Textbox(label="Status", interactive=False)

    # Stage 2: Main Application Dashboard
    with gr.Tabs(visible=False) as main_dashboard:
        # Tab 1: Portfolio
        with gr.Tab("Portfolio") as portfolio_tab:
            with gr.Row():
                gr.Markdown("## Portfolio Summary")
            with gr.Row():
                portfolio_value_tb = gr.Textbox(label="Total Portfolio Value ($)", interactive=False)
                portfolio_pl_tb = gr.Textbox(label="Total Profit / Loss ($)", interactive=False)
                portfolio_cash_tb = gr.Textbox(label="Cash Balance ($)", interactive=False)
            portfolio_refresh_btn = gr.Button("Refresh", variant="secondary")
            holdings_df = gr.Dataframe(
                label="Current Holdings",
                headers=["Symbol", "Quantity", "Current Price", "Total Value"],
                datatype=["str", "number", "str", "str"],
                interactive=False
            )

        # Tab 2: Cash Management
        with gr.Tab("Cash Management") as cash_management_tab:
            with gr.Row():
                gr.Markdown("## Manage Your Cash")
            cash_management_balance_tb = gr.Textbox(label="Current Cash Balance", interactive=False)
            cash_amount_num = gr.Number(label="Amount ($)", minimum=0.01)
            with gr.Row():
                deposit_btn = gr.Button("Deposit", variant="primary")
                withdraw_btn = gr.Button("Withdraw")
            cash_management_status_box = gr.Textbox(label="Status", interactive=False)

        # Tab 3: Trade
        with gr.Tab("Trade") as trade_tab:
            with gr.Row():
                gr.Markdown("## Execute a Trade")
            trade_action_dd = gr.Dropdown(label="Action", choices=["BUY", "SELL"], value="BUY")
            trade_symbol_tb = gr.Textbox(label="Stock Symbol", placeholder="e.g., AAPL, TSLA, GOOGL")
            trade_quantity_num = gr.Number(label="Quantity", minimum=1, precision=0, value=1)
            execute_trade_btn = gr.Button("Execute Trade", variant="primary")
            trade_status_box = gr.Textbox(label="Status", interactive=False)

        # Tab 4: History
        with gr.Tab("History") as history_tab:
            with gr.Row():
                gr.Markdown("## Transaction History")
            history_df = gr.Dataframe(
                label="All Transactions",
                headers=["Timestamp", "Type", "Symbol", "Quantity", "Price", "Total"],
                datatype=["str", "str", "str", "str", "str", "str"],
                interactive=False,
                height=400
            )

    # --- Event Wiring ---

    # List of components on the portfolio tab to be updated together
    portfolio_outputs = [
        portfolio_value_tb, portfolio_pl_tb, portfolio_cash_tb,
        cash_management_balance_tb, holdings_df
    ]
    
    # 1. Account Creation
    create_account_btn.click(
        fn=handle_create_account,
        inputs=[create_username_tb, create_password_tb, create_deposit_num],
        outputs=[creation_status_box, account_state, creation_view, main_dashboard]
    ).then(
        fn=refresh_portfolio_view,
        inputs=[account_state],
        outputs=portfolio_outputs
    ).then(
        fn=refresh_history_view,
        inputs=[account_state],
        outputs=[history_df]
    )

    # 2. Portfolio Tab Refresh
    portfolio_refresh_btn.click(
        fn=refresh_portfolio_view,
        inputs=[account_state],
        outputs=portfolio_outputs
    )
    portfolio_tab.select(
        fn=refresh_portfolio_view,
        inputs=[account_state],
        outputs=portfolio_outputs
    )

    # 3. History Tab Refresh
    history_tab.select(
        fn=refresh_history_view,
        inputs=[account_state],
        outputs=[history_df]
    )

    # 4. Cash Management Actions
    deposit_btn.click(
        fn=handle_deposit,
        inputs=[account_state, cash_amount_num],
        outputs=[cash_management_status_box, account_state]
    ).then(
        fn=refresh_portfolio_view,
        inputs=[account_state],
        outputs=portfolio_outputs
    ).then(
        fn=refresh_history_view,
        inputs=[account_state],
        outputs=[history_df]
    )

    withdraw_btn.click(
        fn=handle_withdraw,
        inputs=[account_state, cash_amount_num],
        outputs=[cash_management_status_box, account_state]
    ).then(
        fn=refresh_portfolio_view,
        inputs=[account_state],
        outputs=portfolio_outputs
    ).then(
        fn=refresh_history_view,
        inputs=[account_state],
        outputs=[history_df]
    )

    # 5. Trade Action
    execute_trade_btn.click(
        fn=handle_trade,
        inputs=[account_state, trade_action_dd, trade_symbol_tb, trade_quantity_num],
        outputs=[trade_status_box, account_state]
    ).then(
        fn=refresh_portfolio_view,
        inputs=[account_state],
        outputs=portfolio_outputs
    ).then(
        fn=refresh_history_view,
        inputs=[account_state],
        outputs=[history_df]
    )


if __name__ == "__main__":
    app.launch()
```