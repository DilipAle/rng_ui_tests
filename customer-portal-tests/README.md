# Customer Portal Tests

UI test automation for the **Renegade Insurance Customer Portal**.
Tests the customer-facing self-service portal — login, dashboard, policy viewing.

---

## Project Structure

```
customer-portal-tests/
│
├── .env                          # Credentials — NEVER commit this file
├── pytest.ini                    # Test runner config
├── requirements.txt              # All Python dependencies
├── conftest.py                   # Shared fixtures + screenshot-on-failure hook
│
├── config/
│   ├── config.py                 # Loads .env — URL, credentials, browser, headless
│   └── browser_config.py        # Launches Playwright browser
│
├── pages/
│   ├── base/
│   │   └── base_page.py         # Re-exports shared BasePage
│   ├── login/
│   │   └── login_page.py        # Login page — email/password login
│   ├── dashboard/
│   │   └── dashboard_page.py    # Customer dashboard — navigation + summary cards
│   └── policy/
│       └── policy_page.py       # Policy list — view and download policies
│
└── tests/
    └── ui/
        ├── login/
        │   └── test_login.py          # 2 tests: valid + invalid credentials
        ├── dashboard/
        │   └── test_dashboard.py      # 2 tests: loads + navigation visible
        └── policy/
            └── test_policy.py         # 2 tests: list visible + not empty
```

---

## Setup

```bash
# 1. Navigate to this project
cd customer-portal-tests

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
playwright install chromium

# 5. Create .env file
touch .env
```

---

## .env Variables

```env
ENV=qa

QA_PORTAL_URL=https://...
QA_PORTAL_USERNAME=customer@example.com
QA_PORTAL_PASSWORD=yourpassword

BROWSER=chromium
HEADLESS=true
```

---

## Running Tests

```bash
source venv/bin/activate

# Smoke tests
pytest -m smoke -v

# All tests
pytest -v

# Visible browser (debugging)
HEADLESS=false pytest -v

# Specific file
pytest tests/ui/dashboard/test_dashboard.py -v
```

---

## Test Suite

### Login Tests

| Test | Marker | Description |
|---|---|---|
| `test_login_valid_credentials` | smoke | Valid login redirects to dashboard or home |
| `test_login_invalid_credentials` | regression | Wrong credentials show error message |

### Dashboard Tests

| Test | Marker | Description |
|---|---|---|
| `test_dashboard_loads` | smoke | Welcome message visible after login |
| `test_dashboard_navigation_visible` | regression | Policies and Billing nav links present |

### Policy Tests

| Test | Marker | Description |
|---|---|---|
| `test_policy_list_visible` | smoke | Policy list visible after navigating from dashboard |
| `test_policy_list_not_empty` | regression | At least one policy exists in the list |

---

## Writing New Tests

### Step 1 — Create a page object
```python
# pages/billing/billing_page.py
from pages.base.base_page import BasePage

class BillingPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.billing_table = ".billing-history"
        self.pay_button = "button[data-action='pay-now']"

    def is_billing_table_visible(self) -> bool:
        return self.is_visible(self.billing_table)

    def click_pay_now(self):
        self.click(self.pay_button)
        self.page.wait_for_load_state("networkidle")
```

### Step 2 — Create a test
```python
# tests/ui/billing/test_billing.py
import pytest
from pages.dashboard.dashboard_page import DashboardPage
from pages.billing.billing_page import BillingPage

@pytest.mark.smoke
def test_billing_page_loads(login):
    page = login
    dashboard = DashboardPage(page)
    dashboard.go_to_billing()

    billing = BillingPage(page)
    assert billing.is_billing_table_visible(), "Billing table not visible"
```

---

## Allure Report

```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

---

## Dependencies

```
playwright==1.51.0
pytest==9.0.2
pytest-xdist==3.6.1
pytest-rerunfailures==14.0
pytest-html==4.2.0
pytest-metadata==3.1.1
allure-pytest==2.13.5
pyotp==2.9.0
python-dotenv==1.1.0
```
