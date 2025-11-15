---

# Complete User Stories Document  

### **Story 1: User Account Creation**  
**Story Header**  
- **ID:** US001  
- **Title:** User can create an account  
- **User Story Statement:** As a user, I want to create an account so that I can start using the trading simulation platform.  
- **Business Value:** Ensures user onboarding. Allows for personalized tracking of funds and transactions.  
- **Priority:** High  

**Acceptance Criteria**  
- **Given:** A user is on the "Create Account" screen (start page).  
  **When:** They enter a valid username and password and click the “Create Account” button.  
  **Then:** The account is successfully created, and the UI displays a success message: *"Account created successfully!"*.  

- **Given:** A user is on the "Create Account" screen.  
  **When:** They try to create an account with an empty username or password field and click “Create Account.”  
  **Then:** The system prevents account creation and displays an error: *"Username and password cannot be empty."*.  

- **Given:** A username is already taken.  
  **When:** The user attempts to register a new account with that username.  
  **Then:** The UI displays an error: *"Username already exists. Please try a different username."*.  

**UI/UX Specs:**  
- **Wireframe:**  
  - *“Create Account” Screen:*  
    - Two input fields (username, password).  
    - `Gradio` components: `gr.Textbox` for inputs.  
    - Button: `Create Account` (Gradio `gr.Button`).  
    - Success/Error messages below the "Create Account" button using `gr.Label`.  

---

### **Story 2: Depositing Funds**  
**Story Header**  
- **ID:** US002  
- **Title:** User can deposit funds into their account  
- **User Story Statement:** As a user, I want to deposit funds into my account so that I have balance available for transactions.  
- **Business Value:** Enables user to simulate trading by ensuring sufficient funds in the account.  
- **Priority:** High  

**Acceptance Criteria**  
- **Given:** A user is on the "Account Management" screen.  
  **When:** They enter a valid amount (greater than 0) in the “Deposit Funds” field and click the “Deposit” button.  
  **Then:** The balance is updated, and the UI displays a message: *"Deposit successful. New balance: [updated_balance]"*.  

- **Given:** A user is on the "Account Management" screen.  
  **When:** They enter 0 or a negative amount and attempt to deposit.  
  **Then:** The system prevents the deposit request and displays an error: *"Deposit amount must be greater than 0."*.  

**UI/UX Specs:**  
- **Wireframe:**  
  - "Deposit Funds Field" within "Account Management Screen":  
    - Input field for entering the amount (`gr.Number`).  
    - Button "Deposit Funds" (`gr.Button`).  
- Messages: Success/Error messages below the form using `gr.Label`.  

---

### **Story 3: Withdrawing Funds**  
**Story Header**  
- **ID:** US003  
- **Title:** User can withdraw funds without exceeding account balance  
- **User Story Statement:** As a user, I want to withdraw funds from my account so that I can utilize my funds elsewhere.  
- **Business Value:** Core banking functionality ensures realism in the trading simulation.  
- **Priority:** High  

**Acceptance Criteria**  
- **Given:** A user is on the "Account Management" screen.  
  **When:** They request to withdraw an amount less than or equal to their balance.  
  **Then:** The balance is updated, and the system displays: *"Withdrawal successful. New balance: [updated_balance]"*.  

- **Given:** A user is on the "Account Management" screen.  
  **When:** They request to withdraw more than their balance.  
  **Then:** The system prevents the withdrawal request and displays: *"Insufficient balance. Withdrawal amount exceeds your available funds."*.  

**UI/UX Specs:**  
- **Wireframe:**  
  - "Withdraw Funds Field" within "Account Management Screen":  
    - Input field: Amount to withdraw (`gr.Number`).  
    - Button: "Withdraw Funds" (`gr.Button`).  
    - Messages: Success/Error notifications using `gr.Label`.  

---

### **Story 4: Record Share Transactions**  
**Story Header**  
- **ID:** US004  
- **Title:** Record when a user buys or sells shares  
- **User Story Statement:** As a user, I want to record share transactions so that I can track my portfolio.  
- **Business Value:** Records user trades for portfolio management and calculation of profit/loss.  
- **Priority:** High  

**Acceptance Criteria**  
- **Given:** A user enters "Buy," share symbol, quantity, and has sufficient funds for the transaction.  
  **When:** They click the "Submit Transaction" button.  
  **Then:** Their holdings and balance update, and the system displays: *"Transaction successful. Updated balance: [updated_balance]."*.  

- **Given:** A user attempts a "Buy" where the funds are insufficient.  
  **When:** They click “Submit Transaction.”  
  **Then:** The system prevents the transaction and displays: *"Insufficient funds for this transaction."*.  

- **Given:** A user attempts to "Sell" shares they don’t own or insufficient shares.  
  **When:** They click “Submit Transaction.”  
  **Then:** The system prevents the transaction and displays: *"Insufficient shares in your portfolio to sell."*.  

**UI/UX Specs:**  
- **Wireframe:**  
  - Form in "Trade Management" Screen:  
    - Dropdown for Buy/Sell options (`gr.Dropdown`).  
    - Text input for share symbol (`gr.Textbox`).  
    - Number input for quantity (`gr.Number`).  
    - Button: Submit Transaction (`gr.Button`).  
  - Notifications via `gr.Label`.  

---

### **Story 5: Portfolio Value & P/L Calculation**  
**Story Header**  
- **ID:** US005  
- **Title:** Users can view portfolio value and profit/loss  
- **User Story Statement:** As a user, I want to view my portfolio's total value and profit/loss so that I can evaluate my trading performance.  
- **Business Value:** Provides insights to users on their financial status in the simulation.  
- **Priority:** High  

**Acceptance Criteria**  
- **Given:** A user is on the "Portfolio Summary" screen.  
  **When:** They click "Calculate Portfolio Value."  
  **Then:** The system calculates and displays their portfolio's total value and current profit/loss.  

**UI/UX Specs:**  
- **Wireframe:**  
  - Area within "Portfolio Summary Screen":  
    - Static text: Portfolio value and profit/loss (`gr.Label`).  
    - Button for "Calculate Portfolio" (`gr.Button`).  

---

### **Story 6: Transaction History**  
**Story Header**  
- **ID:** US006  
- **Title:** Users can view a list of their transactions  
- **User Story Statement:** As a user, I want to view a transaction history so that I can review my trades over time.  
- **Business Value:** Adds transparency and a historical perspective for the user.  
- **Priority:** Medium  

**Acceptance Criteria**  
- **Given:** A user selects “Transaction History” from the menu.  
  **When:** They are redirected to a new screen.  
  **Then:** A table of all transactions is displayed, including date, type (Buy/Sell), symbol, quantity, and total value ($).  

**UI/UX Specs:**  
- **Wireframe:**  
  - Table-based display for transaction history (`gr.Dataframe`).  

--- 

# Final Notes:  
- All success and error messages must use `gr.Label` components and be testable by QA.  
- Performance should ensure seamless API integration with `get_share_price(symbol)` and handle real-time edge cases (like temporary API failures or slow responses).  
- Accessibility: Ensure all text is accessible via screen readers. Buttons and input fields should use standard focus/tab navigation.  

**End of User Stories Document**