# Renegade UI Test Automation Framework
## Complete Documentation

---

## Table of Contents
1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [How the Framework Works](#how-the-framework-works)
5. [Code Flow — Step by Step](#code-flow--step-by-step)
6. [Configuration](#configuration)
7. [Authentication — TOTP & Trusted IP](#authentication--totp--trusted-ip)
8. [Page Object Model](#page-object-model)
9. [Fixtures](#fixtures)
10. [Tests](#tests)
11. [Running Tests](#running-tests)
12. [Smoke vs Regression](#smoke-vs-regression)
13. [Environment Setup](#environment-setup)
14. [Issues Fixed](#issues-fixed)
15. [CI/CD Considerations](#cicd-considerations)

---

## Overview

This is a UI test automation framework for the **Renegade Insurance** Salesforce application.
It automates end-to-end browser interactions against the QA sandbox environment using
Python, Playwright, and pytest.

**Target Application:** Salesforce Lightning (QA Sandbox)
**URL:** `https://renegadeinsurancellc--qa.sandbox.lightning.force.com`

---

## Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.13 | Language |
| Playwright | 1.51.0 | Browser automation |
| pytest | 9.0.2 | Test runner |
| pyotp | 2.9.0 | TOTP/MFA code generation |
| python-dotenv | 1.1.0 | Load credentials from .env |
| pytest-html | 4.2.0 | HTML test reports |

---

## Project Structure

```
renegade-ui-tests/
│
├── .env                        # Credentials (gitignored — never committed)
├── .gitignore                  # Ignores .env, venv, reports, __pycache__
├── pytest.ini                  # pytest config — test paths and markers
├── requirements.txt            # All dependencies
├── conftest.py                 # Shared fixtures (browser, config, login)
│
├── config/
│   ├── config.py               # Loads env vars — URL, credentials, browser
│   └── browser_config.py       # Launches browser via Playwright
│
├── pages/
│   ├── base/
│   │   └── base_page.py        # BasePage — shared actions (click, fill, goto)
│   ├── login/
│   │   └── login_page.py       # Login page — login, TOTP handling, error messages
│   ├── navigation_tab/
│   │   └── navigation_tab_page.py  # Nav bar — tab navigation methods
│   ├── account/
│   │   ├── account_page.py         # Account type selection
│   │   └── account_creation.py     # Account creation form fields
│   └── billing/
│       └── ascend_checkout.py      # Ascend billing checkout flow
│
└── tests/
    └── ui/
        ├── login/
        │   └── test_login.py           # Login smoke + regression tests
        ├── navigation_tab/
        │   └── test_navigation_tab.py  # Navigation tab smoke tests
        ├── account/
        │   └── test_individual_suspect_prospect_page.py
        └── billing/
            └── test_ascend_checkout.py
```

---

## How the Framework Works

The framework follows the **Page Object Model (POM)** design pattern.

```
Test File
  └── uses Fixtures (conftest.py)
        └── uses Config (config.py) — reads .env
        └── uses BrowserConfig (browser_config.py) — launches browser
        └── uses LoginPage (login_page.py) — handles login + TOTP
              └── extends BasePage (base_page.py) — shared browser actions
  └── uses Page Objects
        └── e.g. NavigationTabPage — feature-specific actions
              └── extends BasePage
```

Every page object inherits from `BasePage` which wraps Playwright actions
(`click`, `fill`, `goto`). This means all tests use the same consistent
interface to interact with the browser.

---

## Code Flow — Step by Step

### When you run `pytest`

```
Step 1 — pytest starts
  → reads pytest.ini
  → finds testpaths = tests/ui/
  → collects all test files

Step 2 — conftest.py loads
  → registers fixtures: setup_browser, config, login

Step 3 — config fixture (scope=session, runs once per session)
  → Config() loads .env via python-dotenv
  → reads ENV=qa
  → sets BASE_URL, USERNAME, PASSWORD, TOTP_SECRET, BROWSER, HEADLESS

Step 4 — setup_browser fixture (scope=function, runs per test)
  → sync_playwright() starts Playwright
  → BrowserConfig reads BROWSER and HEADLESS from config
  → launches chromium (headless or visible)
  → creates new page with viewport 1920x1080
  → yields page to test
  → closes browser after test completes

Step 5 — login fixture (scope=function, runs per test that needs it)
  → receives page from setup_browser
  → navigates to BASE_URL
  → creates LoginPage(page)
  → calls login_with_totp(username, password, totp_secret)
      → fills username field (#username)
      → fills password field (#password)
      → clicks Login button (#Login)
      → waits for page to load
      → checks if URL contains "TotpVerificationUi"
          YES and secret exists → generates 6-digit TOTP code via pyotp
                                → fills input#tc
                                → clicks input#save (Verify button)
          NO or no secret       → skips silently (trusted IP scenario)
  → yields logged-in page to test
  → test runs
  → browser closes (setup_browser teardown)

Step 6 — test runs
  → uses the logged-in page
  → creates page object (e.g. NavigationTabPage)
  → calls page object methods
  → asserts expected outcomes
```

---

## Configuration

### `.env` file (never commit this)

```env
ENV=qa

QA_URL=https://renegadeinsurancellc--qa.sandbox.lightning.force.com/
QA_USERNAME=automation@renegadeinsurance.qa
QA_PASSWORD=yourpassword
QA_TOTP_SECRET=                    # Leave empty if using Trusted IP

BROWSER=chromium                   # chromium | firefox | webkit
HEADLESS=true                      # true = no browser window | false = visible
```

### Supported Environments

| ENV value | Reads from .env |
|---|---|
| `qa` | QA_URL, QA_USERNAME, QA_PASSWORD, QA_TOTP_SECRET |
| `uat` | UAT_URL, UAT_USERNAME, UAT_PASSWORD, UAT_TOTP_SECRET |
| `production` | PROD_URL, PROD_USERNAME, PROD_PASSWORD, PROD_TOTP_SECRET |

Switch environment by changing `ENV=` in `.env` or passing it at runtime:
```bash
ENV=uat pytest -v
```

---

## Authentication — TOTP & Trusted IP

### What is TOTP?
TOTP (Time-Based One-Time Password) is the 6-digit MFA code that refreshes every
30 seconds. Both the server and the framework generate the same code using a shared
secret key + the current time.

### How the framework handles MFA

```
login_with_totp() called
  → username + password submitted
  → page loads
  → Is URL = TotpVerificationUi?
      NO  → trusted IP in place, MFA skipped → continue to app
      YES → totp_secret set?
              YES → pyotp.TOTP(secret).now() generates 6-digit code
                  → fills input#tc (TOTP input field)
                  → clicks input#save (Verify button)
                  → continues to app
              NO  → skips silently (no crash)
```

### Trusted IP Setup (Recommended for Automation)
MFA is bypassed for logins from trusted IP addresses.

```
Salesforce Setup → Security → Network Access → Trusted IP Ranges → New
  Start IP: <your machine IP>
  End IP:   <your machine IP>
  Description: Local Automation Machine
```

Get your IP:
```bash
curl ifconfig.me
```

For CI/CD — add the CI server's outbound IP to the same trusted range.

### When TOTP Secret is Needed
If the machine IP cannot be added to the trusted range, set a valid TOTP secret:
- Must be a valid **base32** string (uppercase A-Z and digits 2-7 only)
- Get it from your authenticator app or during Salesforce MFA setup
- Verify it works: `python3 -c "import pyotp; print(pyotp.TOTP('YOUR_SECRET').now())"`

---

## Page Object Model

### BasePage (`pages/base/base_page.py`)
The foundation all page objects inherit from. Wraps Playwright actions.

```python
BasePage
  ├── click(selector)          # Click an element
  ├── fill(selector, value)    # Type into an input
  ├── goto(url)                # Navigate to URL
  ├── get_title()              # Get page title
  └── wait_for_element(selector, timeout)  # Wait for element to appear
```

### LoginPage (`pages/login/login_page.py`)
Handles all login-related actions including TOTP.

```python
LoginPage(BasePage)
  ├── login(username, password)                          # Basic login
  ├── login_with_totp(username, password, totp_secret)  # Login + TOTP handling
  ├── handle_totp(totp_secret)                          # Detect and fill TOTP
  ├── login_with_invalid_credentials(username, password) # Login + wait for error
  ├── is_logged_in()                                     # Check login success
  └── get_error_message()                                # Get error text
```

### NavigationTabPage (`pages/navigation_tab/navigation_tab_page.py`)
Handles Salesforce navigation bar tab clicks.

```python
NavigationTabPage(BasePage)
  ├── go_to_home()
  ├── go_to_accounts()
  ├── go_to_contacts()
  ├── go_to_mypartners()
  ├── go_to_policies()
  ├── go_to_dashboards()
  └── go_to_tasks()
```

---

## Fixtures

Fixtures are defined in `conftest.py` and shared across all tests automatically.

### `config` (scope: session)
Runs **once per test session**. Loads the `.env` file and returns a `Config` object
with all settings. Reused across all tests — no repeated file reads.

### `setup_browser` (scope: function)
Runs **once per test**. Starts Playwright, launches the configured browser with
a 1920x1080 viewport, and yields the page. Closes the browser after the test.

### `login` (scope: function)
Runs **once per test that uses it**. Depends on `setup_browser` and `config`.
Navigates to the app, performs login with TOTP handling, and yields the
authenticated page to the test.

**Usage in test:**
```python
def test_something(login):       # uses login fixture → already logged in
    page = login
    ...

def test_something(setup_browser, config):  # uses raw browser → not logged in
    page = setup_browser
    page.goto(config.BASE_URL)
    ...
```

---

## Tests

### Login Tests (`tests/ui/login/test_login.py`)

| Test | Marker | What it verifies |
|---|---|---|
| `test_login_valid_credentials` | smoke | Happy path login succeeds, app loads |
| `test_login_invalid_username` | regression | Error shown for wrong username |
| `test_login_invalid_password` | regression | Error shown for wrong password |
| `test_login_empty_password` | regression | Error shown for empty password |

### Navigation Tab Tests (`tests/ui/navigation_tab/test_navigation_tab.py`)

| Test | Marker | What it verifies |
|---|---|---|
| `test_navigation_tabs` | smoke | Home, Accounts, Contacts tabs are clickable |

---

## Running Tests

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (first time only)
playwright install
```

### Run Commands

```bash
# All tests
pytest -v

# Smoke tests only (fast, ~30 seconds)
pytest -m smoke -v

# Regression tests only
pytest -m regression -v

# Specific test file
pytest tests/ui/login/test_login.py -v

# Specific test
pytest tests/ui/login/test_login.py::test_login_valid_credentials -v

# With visible browser (useful for debugging)
HEADLESS=false pytest -v

# Generate HTML report
pytest -v --html=report.html
```

---

## Smoke vs Regression

| | Smoke | Regression |
|---|---|---|
| **Purpose** | Verify core app is working | Verify full feature coverage |
| **When to run** | Every deployment | Nightly or pre-release |
| **Speed** | Fast — minimal tests | Slower — thorough |
| **Tests include** | Happy path only | Edge cases + negative scenarios |
| **Marker** | `@pytest.mark.smoke` | `@pytest.mark.regression` |

**Rule of thumb when writing new tests:**
- "Does this test verify the app is alive and working?" → `smoke`
- "Does this test verify what happens when something goes wrong?" → `regression`

---

## Environment Setup

### First Time Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd renegade-ui-tests

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
playwright install

# 5. Create .env file (never committed to git)
touch .env
# Add credentials — see Configuration section above

# 6. Run smoke tests to verify setup
pytest -m smoke -v
```

### Files Never Committed to Git
```
.env              ← credentials and secrets
venv/             ← virtual environment
__pycache__/      ← Python bytecode
.pytest_cache/    ← pytest cache
allure-results/   ← test reports
report.html       ← HTML report
```

---

## Issues Fixed

| Issue | Root Cause | Fix Applied |
|---|---|---|
| TOTP page blocked login | `wait_for_url` waits for future navigation — page already on TOTP URL | Changed to `page.url` check |
| TOTP selector wrong | Actual input is `input#tc`, not `input#totpCode` | Updated selector |
| Error message assertions failing | Salesforce prepends `"Error: "` to messages | Updated expected strings |
| Nav tabs not clickable | Default viewport (1280px) too narrow — tabs hidden in overflow | Set viewport to 1920x1080 |
| `TOTP_SECRET` crashed config | Config raised error if secret missing | Made TOTP_SECRET optional |
| `requirements.txt` incomplete | pytest, pyotp, pytest-html were missing | Added all used packages |
| `.gitignore` incomplete | pytest cache, reports not ignored | Added missing entries |

---

## CI/CD Considerations

When moving to CI/CD (GitHub Actions, Jenkins, etc.):

### Option 1 — Add CI Server IP to Salesforce Trusted Range (Recommended)
```
Salesforce Setup → Security → Network Access → Trusted IP Ranges
  → Add the CI server's outbound IP
```
No code changes needed. Framework behaves identically to local.

### Option 2 — Use TOTP Secret as CI Environment Variable
```yaml
# GitHub Actions example
env:
  ENV: qa
  QA_USERNAME: ${{ secrets.QA_USERNAME }}
  QA_PASSWORD: ${{ secrets.QA_PASSWORD }}
  QA_TOTP_SECRET: ${{ secrets.QA_TOTP_SECRET }}
```
Store secrets in your CI platform's secret manager — never in code.

### Headless Mode
CI/CD always runs headless. Ensure `.env` or CI env has:
```
HEADLESS=true
```
