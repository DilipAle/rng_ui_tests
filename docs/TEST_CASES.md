# Test Cases — Auto360 Automation Framework

Complete inventory of all automated test cases across the Auto360 framework.

Last updated: March 2026

---

## Table of Contents

1. [Summary](#1-summary)
2. [Renegade UI Tests — Salesforce Lightning](#2-renegade-ui-tests--salesforce-lightning)
   - [Login](#21-login)
   - [Navigation Tab Bar](#22-navigation-tab-bar)
   - [Account Creation](#23-account-creation)
   - [New Business Pipeline — Intake Form](#24-new-business-pipeline--intake-form)
   - [Policy — Intake Form](#25-policy--intake-form)
   - [E2E — Submission Flow](#26-e2e--submission-flow)
3. [Agency Height Tests](#3-agency-height-tests)
4. [Customer Portal Tests](#4-customer-portal-tests)
5. [Salesforce API Tests](#5-salesforce-api-tests)
6. [Test Execution Reference](#6-test-execution-reference)

---

## 1. Summary

| Project | Smoke | Regression | E2E | Total |
|---|---|---|---|---|
| renegade-ui-tests | 12 | 3 | 2 | **17** |
| agency-height-tests | — | — | — | TBD |
| customer-portal-tests | — | — | — | TBD |
| salesforce-api-tests | — | — | — | TBD |

**CI/CD runs:** Smoke + E2E on every push/PR · Regression every night at midnight UTC

---

## 2. Renegade UI Tests — Salesforce Lightning

**Target:** Renegade Insurance Salesforce QA Sandbox
**App type:** Salesforce Lightning (browser-based CRM)
**Run from:** `renegade-ui-tests/`

---

### 2.1 Login

**File:** `tests/ui/login/test_login.py`
**Page Object:** `pages/login/login_page.py`

| ID | Test Name | Marker | Description |
|---|---|---|---|
| TC-001 | `test_login_valid_credentials` | `smoke` | Valid username and password logs in successfully |
| TC-002 | `test_login_invalid_username` | `regression` | Invalid username shows Salesforce error message |
| TC-003 | `test_login_invalid_password` | `regression` | Invalid password shows Salesforce error message |
| TC-004 | `test_login_empty_password` | `regression` | Empty password shows blank-password error |

#### TC-001 — Valid Credentials Login
- **Marker:** `smoke`
- **Fixture:** `login` (pre-authenticated)
- **Steps:**
  1. Navigate to QA sandbox URL
  2. Submit valid username and password
  3. Handle TOTP/MFA if prompted (automatic via pyotp)
  4. Wait for `My Agency` nav element
- **Assertion:** `//span[@title='My Agency']` is visible on the page
- **Expected result:** User lands on the authenticated Salesforce home page
- **Teardown:** None (read-only)

#### TC-002 — Invalid Username
- **Marker:** `regression`
- **Fixture:** `setup_browser` (raw unauthenticated browser)
- **Steps:**
  1. Navigate to QA sandbox URL
  2. Submit `invalid_user` as username with the real password
- **Assertion:** Error message equals `"Error: Please check your username and password. If you still can't log in, contact your Salesforce administrator."`
- **Expected result:** Login page stays open with the Salesforce error banner
- **Teardown:** None

#### TC-003 — Invalid Password
- **Marker:** `regression`
- **Fixture:** `setup_browser`
- **Steps:**
  1. Navigate to QA sandbox URL
  2. Submit real username with `invalid_pass` as password
- **Assertion:** Same error message as TC-002
- **Expected result:** Login page stays open with the Salesforce error banner
- **Teardown:** None

#### TC-004 — Empty Password
- **Marker:** `regression`
- **Fixture:** `setup_browser`
- **Steps:**
  1. Navigate to QA sandbox URL
  2. Submit real username with an empty password
- **Assertion:** Error message equals `"Error: Please enter your password."`
- **Expected result:** Login page stays open with the shorter password-required error
- **Teardown:** None

---

### 2.2 Navigation Tab Bar

**File:** `tests/ui/navigation_tab/test_navigation_tab.py`
**Page Object:** `pages/navigation_tab/navigation_tab_page.py`

All tests in this section use the `login` fixture and are marked `smoke`.
Each test clicks one nav tab and asserts the URL changes to the expected section.

| ID | Test Name | Tab Clicked | URL Assertion |
|---|---|---|---|
| TC-005 | `test_home_tab` | Home | URL contains `lightning` |
| TC-006 | `test_accounts_tab` | Accounts | URL contains `Account` or `one.app` or `New_Business_Flow` |
| TC-007 | `test_contacts_tab` | Contacts | URL contains `Contact` or `lightning` |
| TC-008 | `test_mypartners_tab` | My Partners | URL contains `lightning` |
| TC-009 | `test_policies_tab` | Policies | URL contains `lightning` |
| TC-010 | `test_dashboards_tab` | Dashboards | URL contains `Dashboard` or `lightning` |
| TC-011 | `test_tasks_tab` | Tasks | URL contains `Task` or `lightning` |

- **Marker:** `smoke` (all 7 tests)
- **Fixture:** `login` (pre-authenticated)
- **Steps for each:** Click the nav tab → wait for page load → read current URL
- **Assertion:** URL contains the expected keyword
- **Note:** Salesforce is a Single-Page Application (SPA). URL updates asynchronously after tab click. Broad keyword assertions are used because Salesforce sometimes appends redirects or query strings.
- **Teardown:** None (read-only)

---

### 2.3 Account Creation

**File:** `tests/ui/account/test_account_creation.py`
**Page Objects:** `pages/account/account_page.py`, `pages/account/account_creation.py`

| ID | Test Name | Marker | Description |
|---|---|---|---|
| TC-012 | `test_create_individual_account` | `smoke` | Create a new Individual Suspect/Prospect account |
| TC-013 | `test_create_account_validation_errors` | `regression` | Empty form save shows validation errors |

#### TC-012 — Create Individual Account
- **Marker:** `smoke`
- **Fixture:** `login` (pre-authenticated)
- **Test data:** Unique faker-generated name, phone, email (never conflicts with existing records)
- **Steps:**
  1. Click the `Accounts` tab in the nav bar
  2. Click the `New` button
  3. Select `Individual Suspect/Prospect` record type (radio button)
  4. Click `Next` → land on the account creation form
  5. Fill: First Name, Last Name, Phone, Email (all unique faker data)
  6. Click `Save`
  7. Wait for account detail page to load
- **Assertion:** Account detail page heading contains the first name just created
- **Expected result:** Account is created and the detail page shows the account name
- **Teardown:** Delete the created account (keeps QA environment clean)

#### TC-013 — Validation Errors on Empty Save
- **Marker:** `regression`
- **Fixture:** `login` (pre-authenticated)
- **Steps:**
  1. Click the `Accounts` tab
  2. Click `New`
  3. Select `Individual Suspect/Prospect`
  4. Click `Next` without filling any fields
  5. Click `Save` immediately
- **Assertion:** At least one validation error element is visible on the form
- **Expected result:** Form stays open and shows validation error messages for required fields
- **Teardown:** None (no record created)

---

### 2.4 New Business Pipeline — Intake Form

**File:** `tests/ui/new_business_pipeline/test_intake_form.py`
**Page Object:** `pages/new_business_pipeline/new_business_pipeline_page.py`

| ID | Test Name | Marker | Description |
|---|---|---|---|
| TC-014 | `test_send_intake_form_button_visible` | `smoke` | Pre-qualification record in pipeline shows the Send Intake Form button |

#### TC-014 — Send Intake Form Button Visible in Pipeline
- **Marker:** `smoke`
- **Fixture:** `login` (pre-authenticated)
- **Steps:**
  1. Click the `Pipelines` tab in the nav bar
  2. Click the `Prospects` sub-tab
  3. Filter by status `Pre-Qualification` using the Status dropdown
  4. Click `Apply` to refresh the list
  5. Open the first record in the filtered list
- **Assertion:** The `Send Intake Form` button is present on the policy detail page
- **Expected result:** At least one Pre-qualification policy exists in the pipeline and the Send Intake Form button is visible on its detail page
- **Note:** This test is read-only — it does not click the button or change any state. The button may be active or disabled depending on whether the intake form was already sent for this record.
- **Teardown:** None (read-only)

---

### 2.5 Policy — Intake Form

**File:** `tests/ui/policy/test_policy_intake_form.py`
**Page Objects:** `pages/account/account_page.py`, `pages/account/account_creation.py`, `pages/policy/policy_intake_form_page.py`

| ID | Test Name | Marker | Description |
|---|---|---|---|
| TC-015 | `test_policy_send_intake_form_cta_visible` | `smoke` | Policy page shows Send Intake Form CTA as active |
| TC-016 | `test_policy_intake_form_full_flow` | `e2e` | Full intake form flow: send → disabled → reload → status + Resend → resend |

Both tests use a shared helper `_create_account_and_navigate_to_policy()` which:
1. Creates an Individual account with physical address and LOBs (Auto, Home, Trucking)
2. Salesforce automatically creates a Pre-qualification policy linked to the account
3. Navigates to that linked policy's detail page

#### TC-015 — Send Intake Form CTA Visible (Smoke)
- **Marker:** `smoke`
- **Fixture:** `login` (pre-authenticated)
- **Prerequisites:** Account with LOBs + physical address created in setup
- **Steps:**
  1. Create Individual account with Auto + Home + Trucking LOBs and physical address
  2. Navigate to the linked Pre-qualification policy
  3. Check the `Send Intake Form` button visibility
  4. Check button active/disabled state
  5. Check that the Intake Form Status component is NOT visible yet
- **Assertions:**
  - `Send Intake Form` CTA is visible on the policy page
  - `Send Intake Form` CTA is active (not disabled)
  - Intake Form Status component is not yet visible (form not sent yet)
- **Expected result:** Policy shows an active Send Intake Form button with no status component
- **Teardown:** Delete the created account (linked policy is removed with it)

#### TC-016 — Full Intake Form Flow (E2E)
- **Marker:** `e2e`
- **Fixture:** `login` (pre-authenticated)
- **Steps:**
  1. Create Individual account (Auto + Home + Trucking LOBs + physical address)
  2. Navigate to the linked Pre-qualification policy
  3. **Step 1 — Verify CTA active:** `Send Intake Form` is visible and active
  4. **Step 2 — Send form:** Click `Send Intake Form` → confirm modal → assert CTA goes disabled
  5. **Step 3 — Reload and verify:** Reload page → assert Intake Form Status component appears → assert `Resend` CTA visible → assert `Send Intake Form` still disabled
  6. **Step 4 — Resend:** Click `Resend` → confirm modal → assert `Resend` remains available
- **Assertions (in order):**
  - CTA visible and active before sending
  - CTA disabled immediately after sending (no reload needed)
  - Status component visible after reload
  - Resend CTA visible after reload
  - Send Intake Form CTA still disabled after reload
  - Resend CTA still available after resending (user can resend multiple times)
- **Expected result:** Full intake form send → resend cycle completes successfully
- **Teardown:** Delete the created account

---

### 2.6 E2E — Submission Flow

**File:** `tests/ui/e2e/test_submission_flow.py`
**Page Objects:** `pages/submission/submission_page.py`, `pages/policy/policy_page.py`

| ID | Test Name | Marker | Description |
|---|---|---|---|
| TC-017 | `test_submission_new_account_to_sold` | `e2e` | Full submission: new account → policy → moved to Sold |

#### TC-017 — Full Submission Flow
- **Marker:** `e2e`
- **Fixture:** `login` (pre-authenticated)
- **Test data:** Loaded from `tests/ui/e2e/test_data/new_account.json`
- **Steps:**
  1. Start a new submission via `SubmissionPage`
  2. Fill account information from test data
  3. Add policy via `PolicyPage`
  4. Move policy to `Sold` status
  5. Verify welcome email sent _(TODO: email verification not yet implemented)_
- **Expected result:** Account is created, policy added, and status moved to Sold
- **Status:** Partially implemented (email verification step is pending)

---

## 3. Agency Height Tests

**Target:** Agency Height Insurance Agent Portal
**Run from:** `agency-height-tests/`

Test cases coming soon — framework is in place and ready for test implementation.

---

## 4. Customer Portal Tests

**Target:** Customer Self-Service Portal
**Run from:** `customer-portal-tests/`

Test cases coming soon — framework is in place and ready for test implementation.

---

## 5. Salesforce API Tests

**Target:** Salesforce REST API (no browser)
**Run from:** `salesforce-api-tests/`
**Client:** `simple-salesforce` Python library

Test cases cover:
- Account CRUD operations via API
- Policy creation and status updates
- Submission flow API endpoints

Full API test case documentation coming soon.

---

## 6. Test Execution Reference

### Run by project
```bash
# Renegade UI Tests
cd renegade-ui-tests
pytest -v

# Agency Height Tests
cd agency-height-tests
pytest -v

# Customer Portal Tests
cd customer-portal-tests
pytest -v

# Salesforce API Tests
cd salesforce-api-tests
pytest -v
```

### Run by marker
```bash
# Smoke tests only (fast, critical path)
pytest -m smoke -v

# E2E tests only (full business flows)
pytest -m e2e -v

# Smoke + E2E combined (CI/CD default)
pytest -m "smoke or e2e" -v

# Regression tests (full coverage, run nightly)
pytest -m regression -v

# All tests
pytest -v
```

### Run a single test
```bash
pytest tests/ui/login/test_login.py::test_login_valid_credentials -v
```

### Debug with visible browser
```bash
HEADLESS=false pytest tests/ui/account/test_account_creation.py -v
```

### View Allure report after a run
```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

### Run specific test IDs from this document
| Test ID | Command |
|---|---|
| TC-001 to TC-004 | `pytest tests/ui/login/ -v` |
| TC-005 to TC-011 | `pytest tests/ui/navigation_tab/ -v` |
| TC-012 to TC-013 | `pytest tests/ui/account/test_account_creation.py -v` |
| TC-014 | `pytest tests/ui/new_business_pipeline/ -v` |
| TC-015 to TC-016 | `pytest tests/ui/policy/ -v` |
| TC-017 | `pytest tests/ui/e2e/ -v` |

---

## CI/CD Schedule

| Workflow | Trigger | Tests Run |
|---|---|---|
| `ci.yml` | Every push to `main`/`develop`, every PR | Smoke + E2E |
| `nightly.yml` | Daily at midnight UTC, manual trigger | Regression |

**Allure report:** Published to GitHub Pages after every CI run.
**Failure screenshots:** Uploaded as CI artifact (7-day retention) when any test fails.
**Email report:** Sent to QA lead after every CI run.

---

*For setup instructions see [CONTRIBUTING.md](../CONTRIBUTING.md).
For the technical reference see [README.md](../README.md).*
