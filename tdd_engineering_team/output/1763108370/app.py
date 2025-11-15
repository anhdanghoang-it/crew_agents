import gradio as gr
from accounts import Account

accounts = {}

def create_account(username, email, password, confirm_password):
    if not username or not email or not password or not confirm_password:
        return {"success": False, "message": "All mandatory fields are required."}
    if password != confirm_password:
        return {"success": False, "message": "Passwords do not match."}
    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(not char.isalnum() for char in password):
        return {"success": False, "message": "Password must be at least 8 characters long and include one number and one special character."}
    if username in accounts:
        return {"success": False, "message": "Username already exists."}
    accounts[username] = Account(username, email, password)
    return {"success": True, "message": "Your account has been created!"}

def deposit_funds(username, amount):
    if username not in accounts:
        return {"success": False, "message": "Account not found."}
    try:
        response = accounts[username].deposit_funds(amount)
        return response
    except Exception as e:
        return {"success": False, "message": str(e)}

def buy_shares(username, symbol, quantity):
    if username not in accounts:
        return {"success": False, "message": "Account not found."}
    try:
        response = accounts[username].buy_shares(symbol, quantity, get_share_price)
        return response
    except Exception as e:
        return {"success": False, "message": str(e)}

with gr.Blocks() as app:
    gr.Markdown("# Trading Simulation Platform")
    gr.Markdown("Manage your account: Create accounts, deposit funds, and trade shares.")

    with gr.Tab("Create Account"):
        username = gr.Textbox(label="Username", placeholder="Enter your username")
        email = gr.Textbox(label="Email", placeholder="Enter your email")
        password = gr.Textbox(label="Password", placeholder="Enter your password")
        confirm_password = gr.Textbox(label="Confirm Password", placeholder="Re-enter your password")
        create_account_button = gr.Button("Create Account")
        create_account_output = gr.Textbox(label="Status")

        def create_account_backend(username, email, password, confirm_password):
            response = create_account(username, email, password, confirm_password)
            return response["message"]

        create_account_button.click(create_account_backend, [username, email, password, confirm_password], create_account_output)

    with gr.Tab("Deposit Funds"):
        username_deposit = gr.Textbox(label="Username", placeholder="Enter your username")
        deposit_amount = gr.Number(label="Amount", placeholder="Enter amount to deposit")
        deposit_button = gr.Button("Deposit Funds")
        deposit_output = gr.Textbox(label="Status")

        def deposit_funds_backend(username, amount):
            response = deposit_funds(username, amount)
            return response["message"]

        deposit_button.click(deposit_funds_backend, [username_deposit, deposit_amount], deposit_output)

    with gr.Tab("Buy Shares"):
        username_buy = gr.Textbox(label="Username", placeholder="Enter your username")
        stock_symbol = gr.Textbox(label="Stock Symbol", placeholder="Enter stock symbol (e.g., AAPL)")
        quantity = gr.Number(label="Quantity", placeholder="Enter quantity to buy")
        buy_button = gr.Button("Buy Shares")
        buy_output = gr.Textbox(label="Status")

        def buy_shares_backend(username, symbol, quantity):
            response = buy_shares(username, symbol, quantity)
            return response["message"]

        buy_button.click(buy_shares_backend, [username_buy, stock_symbol, quantity], buy_output)

    gr.Markdown("## Demo Examples")
    gr.Examples(
        examples=[
            ["user123", "user@example.com", "Pass#123", "Pass#123"],
            ["JohnDoe", "john@example.com", "Secure#123", "Secure#123"]
        ],
        inputs=[username, email, password, confirm_password]
    )

if __name__ == "__main__":
    app.launch()