<!-- File: renegade-ui-tests/tests/ui/login/test_login.py -->

# Renegade : Login

## Before Each Test
- No pre-authentication — each test starts from a raw browser (`setup_browser` fixture)
- Navigate to `config.BASE_URL` at the start of each test

---

## 1. Valid Login (smoke)

### 1.1 Can log in with valid credentials and reach the home page
- Navigate to `config.BASE_URL`
- Fill `config.USERNAME` into `#username`
- Fill `config.PASSWORD` into `#password`
- Click `#Login`
- If the page URL contains `"TotpVerificationUi"`, generate a 6-digit TOTP code from `config.TOTP_SECRET` and submit it via `input#tc` then click `input#save`
- The Salesforce home page loads
- `//span[@title='My Agency']` is visible within 30 seconds — confirms authenticated

---

## 2. Invalid Credentials (regression)

### 2.1 Shows an error when the username is invalid
- Navigate to `config.BASE_URL`
- Fill `"invalid_user"` into `#username`
- Fill `config.PASSWORD` into `#password`
- Click `#Login`
- Wait for `div#error` to appear (up to 30 seconds)
- The error text is exactly:
  `"Error: Please check your username and password. If you still can't log in, contact your Salesforce administrator."`

### 2.2 Shows an error when the password is incorrect
- Navigate to `config.BASE_URL`
- Fill `config.USERNAME` into `#username`
- Fill `"invalid_pass"` into `#password`
- Click `#Login`
- Wait for `div#error` to appear (up to 30 seconds)
- The error text is exactly:
  `"Error: Please check your username and password. If you still can't log in, contact your Salesforce administrator."`

### 2.3 Shows an error when the password field is empty
- Navigate to `config.BASE_URL`
- Fill `config.USERNAME` into `#username`
- Leave `#password` empty
- Click `#Login`
- Wait for `div#error` to appear (up to 30 seconds)
- The error text is exactly:
  `"Error: Please enter your password."`
