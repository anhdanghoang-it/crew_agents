# **Complete User Stories Document**

---

## **User Story 1: Create Account**

### **Story Header**
- **ID:** US1  
- **Title:** Create a user account  
- **User Story Statement:** As a user, I want to create an account to start using the trading simulation platform.  
- **Business Value:** Ensures that users can access personalized account functionality for their trading activities.  
- **Priority:** High  

### **Acceptance Criteria**
1. **Given-When-Then - Happy Path**
   - **Given** the user navigates to the account creation page,  
   - **When** they provide a valid username, email address, and password,  
   - **Then** the system successfully creates the account and displays a confirmation message: "Account created successfully!"  

2. **Given-When-Then - Edge Cases**
   - **Given** the user provides a username that already exists,  
   - **When** they try to create the account,  
   - **Then** the system displays an error message: "Username already taken. Please choose another."  

   - **Given** the user provides an invalid email address format,  
   - **When** they try to create the account,  
   - **Then** the system displays an error message: "Invalid email address. Please try again."  

   - **Given** the user provides a password that is less than 8 characters,  
   - **When** they try to create the account,  
   - **Then** the system displays an error message: "Password must be at least 8 characters long."  

---

### **UI/UX Specifications**
- **Wireframe/Mockup:**  
  **Account Creation Page:**  
  - Fields:  
    - Username (Text Input)  
    - Email Address (Text Input)  
    - Password (Password Input)  
  - "Create Account" Button (Primary Button Style)  
  - Feedback: Success and error messages displayed below the form fields in a red (error) or green (success) text.

- **Design Components:**  
  - Use Gradio's `Textbox` component for username, email, and password input.  
  - Add a `Button` for "Create Account" with the `click` event for form submission.  

- **Accessibility Checklist:**  
  - Ensure form fields are properly labeled for screen readers (use "for" and "aria-label" attributes).  
  - Button must be keyboard-navigable using tab and enter keys.  
  - Provide color contrast for error and success messages for readability.

---

## **User Story 2: Deposit Funds**

### **Story Header**
- **ID:** US2  
- **Title:** Deposit funds into the account  
- **User Story Statement:** As a user, I want to deposit funds into my account so that I can use them for trading simulations.  
- **Business Value:** Allows users to fund their account and conduct trades.  
- **Priority:** High  

### **Acceptance Criteria**
1. **Given-When-Then - Happy Path**
   - **Given** the user is on their dashboard,  
   - **When** they enter a deposit amount greater than 0 and click "Deposit,"  
   - **Then** the system updates the account balance and displays a confirmation message: "Funds successfully deposited!"  

2. **Given-When-Then - Edge Cases**
   - **Given** the user enters an amount less than or equal to 0,  
   - **When** they click "Deposit,"  
   - **Then** the system shows an error message: "Deposit amount must be greater than 0."  

---

### **UI/UX Specifications**
- **Wireframe/Mockup:**  
  **Deposit Funds Section on Dashboard:**  
  - Field:  
    - Amount (Numeric Input field)  
  - Button: "Deposit"  
  - Feedback: Success and error messages displayed below the deposit button.  

- **Design Components:**  
  - Use Gradio's `Number` component for the input field for amounts.  
  - Use a `Button` labeled "Deposit" for submission.  

- **Accessibility Checklist:**  
  - Numeric input should be keyboard-accessible and compatible with screen-readers.  
  - Provide clear visual feedback (focus state) for the "Deposit" button.  

---

## **User Story 3: Withdraw Funds**

### **Story Header**
- **ID:** US3  
- **Title:** Withdraw funds from the account  
- **User Story Statement:** As a user, I want to withdraw funds from my account so that I can manage my balance.  
- **Business Value:** Ensures fund withdrawal with balance validation to prevent overdraft.  
- **Priority:** High  

### **Acceptance Criteria**
1. **Given-When-Then - Happy Path**
   - **Given** the user is on their dashboard,  
   - **When** they enter a withdrawal amount less than or equal to their balance and click "Withdraw,"  
   - **Then** the system updates the account balance and displays a confirmation message: "Funds successfully withdrawn!"  

2. **Given-When-Then - Edge Cases**
   - **Given** the user enters an amount greater than their balance,  
   - **When** they click "Withdraw,"  
   - **Then** the system shows an error message: "Insufficient balance. Please enter a lower amount."  

   - **Given** the user enters an amount less than or equal to 0,  
   - **When** they click "Withdraw,"  
   - **Then** the system shows an error message: "Withdrawal amount must be greater than 0."  

---

### **UI/UX Specifications**
- **Wireframe/Mockup:**  
  **Withdraw Funds Section on Dashboard:**  
  - Field:  
    - Amount (Numeric Input field)  
  - Button: "Withdraw"  
  - Feedback: Success and error messages displayed below the withdraw button.  

- **Design Components:**  
  - Use Gradio's `Number` component for the input field for amounts.  
  - Use a `Button` labeled "Withdraw" for submission.  

- **Accessibility Checklist:**  
  - Numeric input should be keyboard-accessible and compatible with screen-readers.  
  - Provide clear visual feedback (focus state) for the "Withdraw" button.  

---

## **Additional Stories** *(Summarized, Draft Format for Extended Iterations)*

### Story 4: Record Buying/Selling Shares  
- Acceptance Criteria:  
  - Validate share availability for sell flows.  
  - Restrict purchases based on the user's fund availability using `get_share_price`.  
  - Display all holdings visually in a table (use Gradio's `DataTable`).

### Story 5: Report Holdings and Portfolio Valuation  
- Provide a "Portfolio Summary" section listing total portfolio value, holdings, and real-time profit/loss calculations.

---

This document represents developer-ready user stories for creating an account management system aligned with the defined requirements and Gradio UI. All acceptance criteria cover happy paths, edge cases, and validation flows ensuring clarity for both developers and QA. Delivered to expectation!