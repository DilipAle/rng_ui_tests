<!-- File: renegade-ui-tests/tests/ui/account/test_account_creation.py -->

# Renegade : Account Creation

## Before Each Test
- User is already logged in (`login` fixture — pre-authenticated page)
- Navigate to the Accounts tab via `a[title="Accounts"]`

## After Each Test
- The account created during the test must be deleted via the Salesforce UI
- Do not delete any account that was not created in this test run

---

## 1. Create Individual Account (smoke)

### 1.1 Can create a new Individual Suspect/Prospect account with unique details
- Click the `New` button (`button:has-text("New")`)
- A modal or page appears showing account type options
- Select the `Individual Suspect/Prospect` radio button
- Click `Next` to proceed to the account creation form
- Fill in a **unique** first name using `faker` (e.g. `fake.first_name()`)
- Fill in a **unique** last name using `faker` (e.g. `fake.last_name()`)
- Fill in a **unique** 10-digit US phone number (e.g. `"2" + fake.numerify("#########")`)
- Fill in a **unique** email address using `faker` (e.g. `fake.unique.email()`)
- Click `Save`
- The account detail page loads successfully
- The account name (first name + last name) is visible on the page
- Clean up: delete the created account after the assertion

---

## 2. Validation (regression)

### 2.1 Shows validation errors when required fields are missing
- Click the `New` button
- Select the `Individual Suspect/Prospect` radio button
- Click `Next`
- Leave all fields empty
- Click `Save`
- Validation error messages are visible on the page
- The form does not navigate away (user stays on creation form)

---

## Data Rules
- First name: `fake.first_name()` — unique per run
- Last name: `fake.last_name()` — unique per run
- Phone: `"2" + fake.numerify("#########")` — 10-digit US phone number, area code starts with 2
- Email: `fake.unique.email()` — guaranteed unique per session
- Never use hardcoded names, phones, or emails
