# Auto360 — Team Onboarding & Contribution Guide

This document is for anyone joining the QA automation team.
Start here. Everything else builds on this.

---

## Table of Contents

1. [What This Project Does](#1-what-this-project-does)
2. [How It Is Organized](#2-how-it-is-organized)
3. [How It Works](#3-how-it-works)
4. [Set Up Your Machine](#4-set-up-your-machine)
5. [Run Your First Test](#5-run-your-first-test)
6. [Understand the Test Results](#6-understand-the-test-results)
7. [How to Write a New Test](#7-how-to-write-a-new-test)
8. [Rules Every Contributor Must Follow](#8-rules-every-contributor-must-follow)
9. [CI/CD — What Happens Automatically](#9-cicd--what-happens-automatically)
10. [Common Problems & Fixes](#10-common-problems--fixes)

---

## 1. What This Project Does

Auto360 is the test automation framework for the Renegade Insurance platform.
It runs automated checks across four different applications to catch bugs before
they reach customers.

| Project | What It Tests | How |
|---|---|---|
| `renegade-ui-tests` | Salesforce Lightning — the main internal CRM | Browser (Playwright) |
| `agency-height-tests` | Agency Height — insurance agent portal | Browser (Playwright) |
| `customer-portal-tests` | Customer self-service portal | Browser (Playwright) |
| `salesforce-api-tests` | Salesforce REST API | HTTP requests (no browser) |

### What gets tested in Salesforce (renegade-ui-tests)

- Login (including MFA/TOTP two-factor authentication)
- Navigation — every tab in the nav bar loads correctly
- Account creation — creating a new customer account
- New Business Pipeline — the Send Intake Form button is visible on Pre-qualification records
- Policy Intake Form — sending the form, verifying disabled state, reload, and Resend

### Why automation?

Every deploy to QA, smoke tests run automatically within minutes.
Manual testing the same checklist takes hours. Automation runs it every time, consistently.

---

## 2. How It Is Organized

```
AuotmationAuto360/
│
├── shared/                        # Code shared by all three UI projects
│   ├── base_page.py               # All browser actions (click, fill, wait, etc.)
│   ├── browser_config.py          # Launches the Playwright browser
│   └── config.py                  # Reads .env file settings
│
├── renegade-ui-tests/             # Salesforce Lightning tests
│   ├── config/                    # Renegade-specific config and browser setup
│   ├── pages/                     # Page Objects — one file per screen/feature
│   │   ├── base/base_page.py      # Re-exports shared BasePage (do not edit)
│   │   ├── login/login_page.py
│   │   ├── navigation_tab/navigation_tab_page.py
│   │   ├── account/account_page.py
│   │   ├── account/account_creation.py
│   │   ├── policy/policy_page.py
│   │   ├── policy/policy_intake_form_page.py
│   │   └── new_business_pipeline/new_business_pipeline_page.py
│   ├── tests/ui/                  # Test files — one folder per feature
│   │   ├── login/
│   │   ├── navigation_tab/
│   │   ├── account/
│   │   ├── new_business_pipeline/
│   │   ├── policy/
│   │   └── e2e/
│   ├── conftest.py                # Shared fixtures (browser, login, config)
│   ├── pytest.ini                 # Test runner settings
│   ├── requirements.txt           # Python dependencies
│   └── .env                       # Credentials — NEVER commit this file
│
├── agency-height-tests/           # Agency Height portal tests (same structure)
├── customer-portal-tests/         # Customer portal tests (same structure)
├── salesforce-api-tests/          # Salesforce REST API tests (no browser)
│
├── prompts/                       # Plain-English acceptance criteria for each feature
│   └── renegade-ui-tests/
│       ├── login.md
│       ├── navigation.md
│       ├── account_creation.md
│       ├── intake_form.md
│       └── policy_intake_form.md
│
├── contexts/
│   └── pytest-tester-agent.md    # Rules for AI-assisted test generation
│
├── CLAUDE.md                      # Instructions for Claude Code (AI assistant)
├── README.md                      # Technical reference
├── CONTRIBUTING.md                # This file — team onboarding guide
├── docs/TEST_CASES.md             # Complete test inventory
└── .github/workflows/             # GitHub Actions CI/CD
    ├── ci.yml                     # Smoke + E2E on every push/PR
    └── nightly.yml                # Regression tests every night at midnight UTC
```

---

## 3. How It Works

### The Page Object Model (POM)

This project uses the Page Object Model design pattern.
The idea is simple: **each screen in the app has one Python class that owns all the selectors and actions for that screen.**

Tests never talk to the browser directly. They only talk to page objects.
Page objects talk to the browser through `BasePage`.

```
Test
 └── Page Object (e.g. LoginPage)
       └── BasePage (shared/base_page.py)
             └── Playwright (controls the browser)
```

**Example — LoginPage:**
```python
# pages/login/login_page.py
class LoginPage(BasePage):
    def __init__(self, page):
        self.username_input = "#username"
        self.password_input = "#password"
        self.login_button   = "#Login"

    def login(self, username, password):
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)
```

**Example — Test using LoginPage:**
```python
# tests/ui/login/test_login.py
def test_login_valid_credentials(login):
    page = login   # already logged in — provided by conftest.py fixture
    assert page.is_visible("//span[@title='My Agency']")
```

### Fixtures (conftest.py)

Fixtures are reusable setup steps that pytest injects into tests automatically.

| Fixture | What it does | Scope |
|---|---|---|
| `config` | Reads `.env` (URL, username, password, TOTP secret) | Session (once per run) |
| `setup_browser` | Launches Chromium at 1920×1080 | Function (once per test) |
| `login` | Goes to the app URL, logs in, handles TOTP/MFA, waits for nav bar | Function (once per test) |

`config` is **session-scoped** — credentials are read once per run.
`setup_browser` and `login` are **function-scoped** — each test gets a fresh browser
and a fresh authenticated session. This prevents test state from leaking between tests.

### Test Markers

Markers classify tests so you can run only what you need.

| Marker | When to run | Purpose |
|---|---|---|
| `@pytest.mark.smoke` | Every deploy | Fast, critical path checks |
| `@pytest.mark.regression` | Nightly / pre-release | Full coverage including edge cases |
| `@pytest.mark.e2e` | Every deploy | Full business flow from start to finish |

### MFA / TOTP Login

Salesforce requires two-factor authentication if the machine IP is not whitelisted.
The framework handles this automatically using `pyotp`:
1. After submitting credentials, Salesforce redirects to the TOTP verification page
2. `LoginPage.handle_totp()` generates the 6-digit code from `QA_TOTP_SECRET` in `.env`
3. The code is entered and submitted
4. The fixture then waits for `//span[@title='My Agency']` to confirm login is complete

If the machine IP is in Salesforce's Trusted IP ranges, step 1 is skipped silently.

---

## 4. Set Up Your Machine

### Requirements

- Python 3.13
- Git
- Access to the GitHub repository
- `.env` file contents — ask the QA lead for credentials

### Step 1 — Clone the repository

```bash
git clone <repo-url>
cd AuotmationAuto360
```

### Step 2 — Set up the project you want to work on

Each project is independent. Set up only the one you need.

```bash
cd renegade-ui-tests
```

### Step 3 — Create a Python virtual environment

```bash
python3 -m venv venv
```

Activate it:

```bash
# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

You will see `(venv)` in your terminal prompt. Keep this active whenever you work on tests.

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Install Playwright browsers

```bash
playwright install chromium
```

This downloads the Chromium browser that Playwright controls.
Only needed once per machine.

### Step 6 — Create your `.env` file

```bash
touch .env
```

Open it and paste the following (get actual values from the QA lead):

```env
# Environment
ENV=qa

# QA Sandbox URL
QA_URL=https://renegadeinsurancellc--qa.sandbox.lightning.force.com/

# Salesforce credentials
QA_USERNAME=your-automation-username@renegadeinsurance.com.qa
QA_PASSWORD=your-password-here
QA_TOTP_SECRET=your-base32-totp-secret

# Browser settings
BROWSER=chromium
HEADLESS=true
```

> **HEADLESS=true** runs tests without a visible browser window (faster, used in CI).
> **HEADLESS=false** opens a visible browser window (useful for debugging locally).

### Step 7 — Verify setup

```bash
pytest tests/ui/login/test_login.py -v
```

If you see `PASSED` — you are set up correctly.

---

## 5. Run Your First Test

All commands must be run from inside the project folder (e.g. `renegade-ui-tests/`).

### Run smoke tests only (recommended starting point)

```bash
pytest -m smoke -v
```

### Run a single test file

```bash
pytest tests/ui/navigation_tab/test_navigation_tab.py -v
```

### Run a single test by name

```bash
pytest tests/ui/login/test_login.py::test_login_valid_credentials -v
```

### Run with visible browser (for debugging)

```bash
HEADLESS=false pytest tests/ui/login/test_login.py -v
```

### Run all tests

```bash
pytest -v
```

### Run regression tests

```bash
pytest -m regression -v
```

### Run both smoke and e2e

```bash
pytest -m "smoke or e2e" -v
```

---

## 6. Understand the Test Results

### Terminal output

```
PASSED   tests/ui/login/test_login.py::test_login_valid_credentials
FAILED   tests/ui/account/test_account_creation.py::test_create_individual_account
```

- `PASSED` — test ran and all assertions were true
- `FAILED` — test ran but an assertion failed (see the error below)
- `ERROR` — test could not run at all (usually a setup/fixture problem)
- `R` or `RR` — test was retried (flaky — passed on retry, not a real failure)

### Allure report (detailed HTML report)

Generate and open after a test run:

```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

This opens a browser report with steps, screenshots, and pass/fail history.

### Screenshots on failure

When any test fails, a screenshot is automatically saved to:

```
screenshots/<test_name>.png
```

This folder is never committed to git. In CI, it is uploaded as an artifact.

---

## 7. How to Write a New Test

Follow these steps every time you add a new feature test.

### Step 1 — Write the acceptance criteria (optional but recommended)

Create a `.md` file in `prompts/renegade-ui-tests/` describing what the test should verify
in plain English. Keep it simple — one scenario per numbered section.

```markdown
<!-- File: renegade-ui-tests/tests/ui/my_feature/test_my_feature.py -->

# My Feature — Smoke Test

## 1. Verify the widget loads

- Navigate to the Widgets tab
- The widget list loads and at least one row is visible
```

### Step 2 — Create the page object

Create a new file in `pages/` for the screen you are testing.

```
pages/my_feature/my_feature_page.py
```

Rules:
- Always extend `BasePage`
- Define all selectors as instance variables in `__init__`
- Write one method per user action
- Never call Playwright directly — use `self.click()`, `self.fill()`, etc.

```python
from pages.base.base_page import BasePage

class MyFeaturePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.my_tab      = 'a[title="My Tab"]'
        self.widget_row  = 'table tbody tr'

    def go_to_my_tab(self):
        self.wait_for_element(self.my_tab, timeout=15000)
        self.click(self.my_tab)
        self.page.wait_for_load_state("load")

    def is_widget_list_visible(self) -> bool:
        return self.is_visible(self.widget_row)
```

### Step 3 — Add an `__init__.py` to the new folder

```bash
touch pages/my_feature/__init__.py
```

Also create the test folder:

```bash
mkdir -p tests/ui/my_feature
touch tests/ui/my_feature/__init__.py
```

### Step 4 — Write the test

```
tests/ui/my_feature/test_my_feature.py
```

```python
import pytest
from pages.my_feature.my_feature_page import MyFeaturePage


@pytest.mark.smoke
def test_widget_list_loads(login):
    page = login
    feature = MyFeaturePage(page)

    feature.go_to_my_tab()

    assert feature.is_widget_list_visible(), \
        "Expected widget list to be visible on My Tab"
```

Rules:
- Use `login` fixture — it provides an authenticated page
- Use `@pytest.mark.smoke` for fast critical checks
- Use `@pytest.mark.regression` for edge cases and negative tests
- Use `@pytest.mark.e2e` for full end-to-end business flows
- One assertion per test where possible
- Always include a failure message in `assert`

### Step 5 — Run your new test

```bash
pytest tests/ui/my_feature/test_my_feature.py -v
```

Fix any failures, then run the full smoke suite to confirm nothing is broken:

```bash
pytest -m smoke -v
```

### Step 6 — Commit and open a pull request

```bash
git checkout -b feature/my-feature-tests
git add pages/my_feature/ tests/ui/my_feature/ prompts/renegade-ui-tests/my_feature.md
git commit -m "Add smoke test for My Feature widget list"
git push origin feature/my-feature-tests
```

Open a PR to `develop`. CI will run automatically.

---

## 8. Rules Every Contributor Must Follow

### Never call Playwright directly in a test

```python
# WRONG
page.click("button")
page.fill("#username", "user")

# CORRECT — use the page object
login_page.login(username, password)
```

### All selectors live in the page object, not the test

```python
# WRONG — selector in the test
def test_something(login):
    page = login
    page.click('button[title="Save"]')

# CORRECT — selector in page object
def test_something(login):
    page = login
    form = MyFormPage(page)
    form.click_save()
```

### Use unique data — never hardcode names

```python
from faker import Faker
fake = Faker()

# CORRECT
first_name = fake.first_name()
last_name  = fake.last_name()
email      = fake.email()
phone      = "2" + fake.numerify("#########")  # 10-digit US format
```

### Every test that creates data must delete it

```python
def test_create_account(login):
    # ... create account ...
    account_name = f"{first_name} {last_name}"

    assert creation_page.is_save_success_visible()

    # Always clean up
    account_page.delete_account(account_name)
```

### Never commit these files

```
.env                  ← contains passwords and secrets
venv/                 ← Python virtual environment
__pycache__/          ← Python bytecode
.pytest_cache/        ← pytest internal cache
allure-results/       ← raw test report data
allure-report/        ← generated HTML report
screenshots/          ← failure screenshots
```

### Run from inside the project folder

```bash
# CORRECT
cd renegade-ui-tests
pytest -m smoke -v

# WRONG — running from repo root collects all 4 projects and causes conflicts
pytest -m smoke -v
```

---

## 9. CI/CD — What Happens Automatically

### On every push and pull request (`ci.yml`)

1. GitHub spins up a clean Ubuntu machine
2. Python 3.13 is installed
3. Dependencies are installed from `requirements.txt`
4. Playwright Chromium browser is installed
5. `.env` is created from GitHub Secrets (credentials stored securely in GitHub)
6. Smoke tests run: `pytest -m smoke -v`
7. E2E tests run: `pytest -m e2e -v`
8. Allure report is generated and published to GitHub Pages
9. Screenshots uploaded as artifact (kept 7 days) if any test failed
10. Email report sent to QA lead

### Every night (`nightly.yml`)

Same process but runs `regression` tests instead of `smoke`.

### Viewing CI results

- Go to the repository on GitHub
- Click **Actions** tab
- Click the latest run to see logs, artifacts, and Allure report link

### GitHub Secrets required (set by repo admin)

| Secret | Used by |
|---|---|
| `QA_URL`, `QA_USERNAME`, `QA_PASSWORD`, `QA_TOTP_SECRET` | renegade-ui-tests |
| `QA_AH_URL`, `QA_AH_USERNAME`, `QA_AH_PASSWORD` | agency-height-tests |
| `QA_PORTAL_URL`, `QA_PORTAL_USERNAME`, `QA_PORTAL_PASSWORD` | customer-portal-tests |
| `SF_USERNAME`, `SF_PASSWORD`, `SF_SECURITY_TOKEN`, `SF_DOMAIN` | salesforce-api-tests |
| `MAIL_USERNAME`, `MAIL_PASSWORD` | Email reports (all projects) |

---

## 10. Common Problems & Fixes

### "ModuleNotFoundError: No module named 'pages'"

You are running pytest from the wrong directory. Always `cd` into the project first:

```bash
cd renegade-ui-tests
pytest -v
```

### "TimeoutError: waiting for locator to be visible"

The element was not found within the timeout. Common causes:
1. Salesforce is slow — the selector is correct but the page hasn't rendered yet
2. The selector is wrong — inspect the live page with the browser devtools
3. Wrong page — a previous test navigated somewhere unexpected

To debug, run with a visible browser:

```bash
HEADLESS=false pytest tests/ui/my_feature/test_my_feature.py -v
```

### "playwright._impl._errors.TimeoutError: networkidle"

Salesforce's `New_Business_Flow` page makes continuous polling requests and
never reaches `networkidle`. Never use `wait_for_load_state("networkidle")` after
tab navigation in Salesforce. Wait for a specific element instead:

```python
# WRONG for Salesforce Lightning
self.page.wait_for_load_state("networkidle")

# CORRECT — wait for something specific on the page
self.wait_for_element('a[title="Home"]', timeout=15000)
```

### "TOTP / MFA verification timed out"

If Salesforce asks for a verification code and the test fails:
1. Check `QA_TOTP_SECRET` in your `.env` is correct
2. Verify it works: `python3 -c "import pyotp; print(pyotp.TOTP('YOUR_SECRET').now())"`
3. Check your machine clock is accurate (TOTP is time-sensitive — within 30 seconds)

To avoid TOTP entirely: add your machine IP to Salesforce → Setup → Network Access → Trusted IP Ranges.

### Tests pass locally but fail in CI

Most common reasons:
1. GitHub Actions runner IP is not in Salesforce Trusted IP ranges → TOTP triggers
2. A GitHub Secret is missing or incorrect
3. The test depends on specific data that exists locally but not in CI

### "faker not found" or any missing package

```bash
pip install -r requirements.txt
```

If you added a new package, add it to `requirements.txt` with a pinned version:

```
faker==24.0.0
```

---

## Related Documentation

| Document | What's in it |
|---|---|
| [README.md](README.md) | Tech stack, quick start, CI/CD reference |
| [docs/TEST_CASES.md](docs/TEST_CASES.md) | All 17 test cases with step-by-step descriptions and assertions |

---

## Questions?

Contact the QA lead: dilip.ale@renegadeinsurance.com

For issues with this repository: open a GitHub Issue or PR.
