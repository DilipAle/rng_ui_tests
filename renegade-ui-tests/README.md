# Renegade UI Tests

UI test automation for the **Renegade Insurance** Salesforce Lightning application.
Automates end-to-end browser tests against the QA sandbox environment.

**Target:** `https://renegadeinsurancellc--qa.sandbox.lightning.force.com`

---

## Project Structure

```
renegade-ui-tests/
│
├── .env                          # Credentials — NEVER commit this file
├── .gitignore
├── pytest.ini                    # Test runner config (paths, markers, parallel settings)
├── requirements.txt              # All Python dependencies
├── conftest.py                   # Shared fixtures + screenshot-on-failure hook
│
├── config/
│   ├── config.py                 # Loads .env — URL, credentials, browser, headless
│   └── browser_config.py        # Launches Playwright browser
│
├── pages/
│   ├── base/
│   │   └── base_page.py         # Re-exports shared BasePage (click, fill, goto...)
│   ├── login/
│   │   └── login_page.py        # Login page — credentials + TOTP/MFA handling
│   ├── navigation_tab/
│   │   └── navigation_tab_page.py # Salesforce nav bar tab navigation
│   ├── account/
│   │   ├── account_page.py      # Account type selection (radio buttons)
│   │   └── account_creation.py  # Account creation form fields
│   └── billing/
│       └── ascend_checkout.py   # Ascend billing checkout flow
│
└── tests/
    └── ui/
        ├── login/
        │   └── test_login.py              # 4 tests: valid + 3 negative
        ├── navigation_tab/
        │   └── test_navigation_tab.py     # 7 tests: one per nav tab
        └── account/
            └── test_individual_suspect_prospect_page.py
```

---

## Setup

### Prerequisites
- Python 3.13
- Access to Renegade Insurance QA Salesforce sandbox

### First Time Setup

```bash
# 1. Navigate to this project
cd renegade-ui-tests

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
playwright install chromium

# 5. Create .env file (see .env Variables section below)
touch .env
```

---

## .env Variables

Create a `.env` file in the `renegade-ui-tests/` directory:

```env
ENV=qa

# QA Environment
QA_URL=https://renegadeinsurancellc--qa.sandbox.lightning.force.com/
QA_USERNAME=automation@renegadeinsurance.qa
QA_PASSWORD=yourpassword
QA_TOTP_SECRET=                    # Leave empty if your IP is in Salesforce Trusted IP Ranges

# UAT Environment (optional)
UAT_URL=https://...
UAT_USERNAME=...
UAT_PASSWORD=...

# Browser settings
BROWSER=chromium                   # chromium | firefox | webkit
HEADLESS=true                      # true = no window (CI) | false = visible (debugging)
```

**Switch environments at runtime:**
```bash
ENV=uat pytest -m smoke -v
```

---

## MFA / TOTP Setup

Salesforce may require a 6-digit MFA code on login. Two ways to handle it:

### Option A — Trusted IP (Recommended)
Add your machine IP to Salesforce's trusted range — no code needed.
```
Salesforce Setup → Security → Network Access → Trusted IP Ranges → New
  Start IP: <your IP>
  End IP:   <your IP>
```
Get your IP: `curl ifconfig.me`

### Option B — TOTP Secret
Set `QA_TOTP_SECRET` in `.env` with the base32 secret from your authenticator app.
Verify it works:
```bash
python3 -c "import pyotp; print(pyotp.TOTP('YOUR_SECRET').now())"
```

---

## Running Tests

```bash
# Activate venv first
source venv/bin/activate

# Smoke tests only (fast — ~20 seconds)
pytest -m smoke -v

# All tests
pytest -v

# Regression tests only
pytest -m regression -v

# Specific test file
pytest tests/ui/login/test_login.py -v

# Specific single test
pytest tests/ui/login/test_login.py::test_login_valid_credentials -v

# Visible browser (for debugging)
HEADLESS=false pytest -m smoke -v

# Serial mode (no parallelism — useful for debugging)
pytest -m smoke -v -n 0

# Generate HTML report
pytest -v --html=report.html
```

---

## Test Results & Reporting

### Allure Report (recommended)
```bash
# After running tests, allure-results/ is auto-generated
allure generate allure-results --clean -o allure-report
allure open allure-report
```

### Screenshots on Failure
When a test fails, a full-page screenshot is automatically saved to:
```
screenshots/<test_name>.png
```
The `screenshots/` directory is only created when a test fails.

---

## Test Suite

### Login Tests (`tests/ui/login/test_login.py`)

| Test | Marker | Description |
|---|---|---|
| `test_login_valid_credentials` | smoke | Happy path — valid login succeeds |
| `test_login_invalid_username` | regression | Wrong username shows error |
| `test_login_invalid_password` | regression | Wrong password shows error |
| `test_login_empty_password` | regression | Empty password shows error |

### Navigation Tab Tests (`tests/ui/navigation_tab/test_navigation_tab.py`)

| Test | Marker | Description |
|---|---|---|
| `test_home_tab` | smoke | Home tab navigates correctly |
| `test_accounts_tab` | smoke | Accounts tab navigates correctly |
| `test_contacts_tab` | smoke | Contacts tab navigates correctly |
| `test_mypartners_tab` | smoke | My Partners tab navigates correctly |
| `test_policies_tab` | smoke | Policies tab navigates correctly |
| `test_dashboards_tab` | smoke | Dashboards tab navigates correctly |
| `test_tasks_tab` | smoke | Tasks tab navigates correctly |

---

## Writing New Tests

### Step 1 — Create a page object
```python
# pages/my_feature/my_feature_page.py
from pages.base.base_page import BasePage

class MyFeaturePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.submit_button = "button[type='submit']"

    def submit(self):
        self.click(self.submit_button)
        self.page.wait_for_load_state("load")
```

### Step 2 — Create a test file
```python
# tests/ui/my_feature/test_my_feature.py
import pytest
from pages.my_feature.my_feature_page import MyFeaturePage

@pytest.mark.smoke
def test_feature_works(login):
    page = login
    feature = MyFeaturePage(page)
    feature.submit()
    assert feature.is_visible(".success"), "Expected success element"
```

### Step 3 — Run it
```bash
pytest tests/ui/my_feature/ -v
```

---

## Parallel Execution

Tests run in parallel by default (configured in `pytest.ini`):
```ini
addopts = -n auto --reruns 2 --reruns-delay 2 --alluredir=allure-results
```
- `-n auto` — uses all available CPU cores
- `--reruns 2` — retries failed tests up to 2 times
- `--reruns-delay 2` — waits 2 seconds between retries

To disable parallelism for debugging:
```bash
pytest -v -n 0
```

---

## Dependencies

```
playwright==1.51.0          # Browser automation
pytest==9.0.2               # Test runner
pytest-xdist==3.6.1         # Parallel execution
pytest-rerunfailures==14.0  # Auto-retry on failure
pytest-html==4.2.0          # HTML reports
pytest-metadata==3.1.1      # Report metadata
allure-pytest==2.13.5       # Allure reporting
pyotp==2.9.0                # TOTP/MFA code generation
python-dotenv==1.1.0        # Load .env file
```
