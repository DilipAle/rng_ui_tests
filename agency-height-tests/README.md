# Agency Height Tests

UI test automation for the **Agency Height** insurance portal.
Automates end-to-end browser tests for the agency-facing submission and quote workflows.

---

## Project Structure

```
agency-height-tests/
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
│   ├── submission/
│   │   └── submission_page.py   # New submission creation flow
│   └── quote/
│       └── quote_page.py        # Quote review and binding
│
└── tests/
    └── ui/
        ├── login/
        │   └── test_login.py          # 2 tests: valid + invalid credentials
        ├── submission/
        │   └── test_submission.py     # 3 tests: create, list, form validation
        └── quote/
            └── test_quote.py          # 2 tests: visibility + premium value
```

---

## Setup

```bash
# 1. Navigate to this project
cd agency-height-tests

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

QA_AH_URL=https://...
QA_AH_USERNAME=your_username@agency.com
QA_AH_PASSWORD=yourpassword

BROWSER=chromium
HEADLESS=true
```

**Switch environments:**
```bash
ENV=uat pytest -m smoke -v
```

---

## Running Tests

```bash
source venv/bin/activate

# Smoke tests
pytest -m smoke -v

# All tests
pytest -v

# Visible browser
HEADLESS=false pytest -v

# Specific file
pytest tests/ui/submission/test_submission.py -v
```

---

## Test Suite

### Login Tests

| Test | Marker | Description |
|---|---|---|
| `test_login_valid_credentials` | smoke | Valid login redirects to dashboard/submissions |
| `test_login_invalid_credentials` | regression | Wrong credentials show error message |

### Submission Tests

| Test | Marker | Description |
|---|---|---|
| `test_create_new_submission` | smoke | Full submission form filled and submitted |
| `test_submission_list_visible` | regression | Submission list visible after login |
| `test_submission_form_required_fields` | regression | Empty form submission shows validation errors |

### Quote Tests

| Test | Marker | Description |
|---|---|---|
| `test_quotes_visible_after_submission` | smoke | Quote list visible after submission processed |
| `test_quote_has_premium` | regression | First quote has a premium value |

---

## Writing New Tests

### Step 1 — Create a page object
```python
# pages/my_feature/my_feature_page.py
from pages.base.base_page import BasePage

class MyFeaturePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.my_button = "button[data-action='my-action']"

    def click_my_button(self):
        self.click(self.my_button)
        self.page.wait_for_load_state("networkidle")
```

### Step 2 — Create a test
```python
# tests/ui/my_feature/test_my_feature.py
import pytest
from pages.my_feature.my_feature_page import MyFeaturePage

@pytest.mark.smoke
def test_feature(login):
    page = login
    feature = MyFeaturePage(page)
    feature.click_my_button()
    assert feature.is_visible(".success")
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
