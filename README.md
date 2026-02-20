# Auto360 Test Automation Framework

End-to-end test automation framework for the Renegade Insurance platform.
Covers 4 independent projects — 3 UI (browser) and 1 API.

---

## Projects

| Project | Type | Target Application |
|---|---|---|
| `renegade-ui-tests` | UI / Browser | Salesforce Lightning (Renegade Insurance QA sandbox) |
| `agency-height-tests` | UI / Browser | Agency Height insurance portal |
| `customer-portal-tests` | UI / Browser | Customer self-service portal |
| `salesforce-api-tests` | API (no browser) | Salesforce REST API |

---

## Repository Structure

```
AuotmationAuto360/
│
├── shared/                          # Shared code used by all UI projects
│   ├── base_page.py                 # BasePage — all Playwright actions live here
│   ├── browser_config.py            # Launches Playwright browser
│   └── config.py                   # Loads .env settings
│
├── renegade-ui-tests/               # Project 1 — Salesforce Lightning UI
├── agency-height-tests/             # Project 2 — Agency Height UI
├── customer-portal-tests/           # Project 3 — Customer Portal UI
├── salesforce-api-tests/            # Project 4 — Salesforce REST API
│
└── .github/
    └── workflows/
        └── smoke-tests.yml          # CI/CD — runs all 4 projects in parallel
```

---

## Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.13 | Language |
| Playwright | 1.51.0 | Browser automation (UI projects) |
| pytest | 9.0.2 | Test runner |
| pytest-xdist | 3.6.1 | Parallel test execution |
| pytest-rerunfailures | 14.0 | Auto-retry on flaky failures |
| allure-pytest | 2.13.5 | Test reporting |
| pytest-html | 4.2.0 | HTML reports |
| pyotp | 2.9.0 | TOTP/MFA code generation |
| python-dotenv | 1.1.0 | Load credentials from .env |
| simple-salesforce | 1.12.6 | Salesforce REST API client |
| faker | 24.0.0 | Synthetic test data |

---

## Quick Start

### 1. Clone the repository
```bash
git clone <repo-url>
cd AuotmationAuto360
```

### 2. Set up a project (example: renegade-ui-tests)
```bash
cd renegade-ui-tests

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (UI projects only)
playwright install chromium

# Create .env file with credentials (see project README for variables)
touch .env
```

### 3. Run tests
```bash
# Smoke tests only (fast)
pytest -m smoke -v

# All tests
pytest -v

# With visible browser (for debugging)
HEADLESS=false pytest -v
```

### 4. View Allure report
```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

---

## Design Pattern — Page Object Model (POM)

```
Test File
  └── Fixtures (conftest.py)
        ├── config     → loads .env
        ├── setup_browser → launches browser
        └── login      → navigates + authenticates
              └── Page Objects (pages/)
                    ├── LoginPage
                    ├── NavigationTabPage
                    └── ...each extends BasePage
                          └── shared/base_page.py
                                └── Playwright (browser control)
```

Every page object inherits from `shared/base_page.py` which wraps Playwright.
Tests never call Playwright directly — always go through page objects.

---

## Test Markers

| Marker | Purpose | When to run |
|---|---|---|
| `smoke` | Critical path — verify app is alive | Every deploy |
| `regression` | Full coverage — edge cases + negative | Nightly / pre-release |
| `api` | API-level tests (Salesforce project) | Every deploy |

```bash
pytest -m smoke -v        # smoke only
pytest -m regression -v   # regression only
pytest -v                 # all tests
```

---

## CI/CD

GitHub Actions workflow at `.github/workflows/smoke-tests.yml` runs all 4 projects
in parallel on every push to `main` or `develop` and on every pull request.

Each job:
- Installs dependencies
- Installs Playwright browsers (UI jobs)
- Creates `.env` from GitHub Secrets
- Runs `pytest -m smoke -v`
- Generates Allure report (uploaded as artifact, kept 7 days)
- Uploads screenshots on failure (kept 7 days)
- Emails test results to the QA lead

### GitHub Secrets required

| Secret | Used by |
|---|---|
| `ENV` | All projects |
| `QA_URL` | renegade-ui-tests |
| `QA_USERNAME` | renegade-ui-tests |
| `QA_PASSWORD` | renegade-ui-tests |
| `QA_TOTP_SECRET` | renegade-ui-tests |
| `QA_AH_URL` | agency-height-tests |
| `QA_AH_USERNAME` | agency-height-tests |
| `QA_AH_PASSWORD` | agency-height-tests |
| `QA_PORTAL_URL` | customer-portal-tests |
| `QA_PORTAL_USERNAME` | customer-portal-tests |
| `QA_PORTAL_PASSWORD` | customer-portal-tests |
| `SF_USERNAME` | salesforce-api-tests |
| `SF_PASSWORD` | salesforce-api-tests |
| `SF_SECURITY_TOKEN` | salesforce-api-tests |
| `SF_DOMAIN` | salesforce-api-tests |
| `MAIL_USERNAME` | All (email reports) |
| `MAIL_PASSWORD` | All (email reports) |

---

## All Changes Made (Framework Audit Fixes)

### Fix 1 — HEADLESS inversion bug
**Files:** `renegade-ui-tests/config/config.py`, `agency-height-tests/config/config.py`,
`customer-portal-tests/config/config.py`, `shared/config.py`

Before (broken): `HEADLESS=true` in .env ran the browser **headed** (visible)
```python
# WRONG — inverted logic
self.HEADLESS = os.getenv("HEADLESS", "true") == "false"
```
After (correct): `HEADLESS=true` now correctly runs **headless** (no window)
```python
# CORRECT
self.HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
```

---

### Fix 2 — Parallel test execution with pytest-xdist
**Files:** All 4 `requirements.txt`, all 4 `pytest.ini`

Added `pytest-xdist==3.6.1` to all requirements.
Added `addopts` to all `pytest.ini`:
```ini
# UI projects — use all available CPU cores
addopts = -n auto --reruns 2 --reruns-delay 2 --alluredir=allure-results

# Salesforce API — fixed at 2 workers (prevents API rate limit issues)
addopts = -n 2 --reruns 2 --reruns-delay 2 --alluredir=allure-results
```
Result: All 8 smoke tests now run simultaneously in ~19 seconds instead of sequentially.

---

### Fix 3 — Screenshot on failure
**Files:** `renegade-ui-tests/conftest.py`, `agency-height-tests/conftest.py`,
`customer-portal-tests/conftest.py`

Added `pytest_runtest_makereport` hook to all 3 UI `conftest.py` files.
On any test failure, automatically captures a full-page screenshot.
```
screenshots/<test_name>.png
```
- Directory only created when a test actually fails
- Never created on passing runs
- Uploaded as CI/CD artifact (7-day retention)

---

### Fix 4 — GitHub Actions CI/CD workflow
**File:** `.github/workflows/smoke-tests.yml` (new file)

4 parallel jobs — one per project. Each job:
- Triggers on push to `main`/`develop` and pull requests
- Installs dependencies and Playwright browsers
- Creates `.env` from GitHub Secrets
- Runs `pytest -m smoke -v`
- Generates Allure report
- Uploads report + screenshots as artifacts (7-day retention)
- Emails results to QA lead

---

### Fix 5 — Centralized shared BasePage
**Files:** `shared/base_page.py`, all 3 `pages/base/base_page.py`

Before: 3 separate BasePage classes with slightly different methods.
Agency Height had `select_option()` that others lacked.

After: One `shared/base_page.py` is the single source of truth.
Each project's `pages/base/base_page.py` is now a 2-line re-export:
```python
from shared.base_page import BasePage
__all__ = ["BasePage"]
```
`select_option()` added to shared BasePage — now available in all projects.
`sys.path` insert added to all 3 UI `conftest.py` files to make `shared` importable.

---

### Fix 6 — Auto-retry flaky tests with pytest-rerunfailures
**Files:** All 4 `requirements.txt`

Added `pytest-rerunfailures==14.0` to all requirements.
`--reruns 2 --reruns-delay 2` in `addopts` (from Fix 2) activates it:
- Any failing test is retried up to 2 times
- 2-second delay between retries
- Only reported as failed if it fails all 3 attempts

---

### Fix 7 — Allure reporting
**Files:** All 4 `requirements.txt`, all 4 `pytest.ini`, `.github/workflows/smoke-tests.yml`

Added `allure-pytest==2.13.5` to all requirements.
Added `--alluredir=allure-results` to all `pytest.ini` addopts.
CI/CD generates and uploads Allure HTML report after every run.

Local usage:
```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

---

### Fix 8 — .gitignore cleanup
**File:** `renegade-ui-tests/.gitignore`

Added missing entries:
```
allure-report/    # generated HTML report
screenshots/      # failure screenshots
```

---

### Fix 9 — Code documentation
**Files:** 14 files across all 4 projects

Added module-level docstrings, class docstrings, and method docstrings to:
- `shared/base_page.py`, `shared/config.py`, `shared/browser_config.py`
- All 4 `conftest.py` files
- `renegade-ui-tests/config/config.py`
- `renegade-ui-tests/pages/base/base_page.py`
- `renegade-ui-tests/pages/login/login_page.py`
- `renegade-ui-tests/pages/navigation_tab/navigation_tab_page.py`
- `renegade-ui-tests/tests/ui/login/test_login.py`
- `renegade-ui-tests/tests/ui/navigation_tab/test_navigation_tab.py`
- `salesforce-api-tests/clients/salesforce_client.py`
- `salesforce-api-tests/utils/data_factory.py`

---

## Writing New Tests

### 1. Add a page object
```python
# pages/my_feature/my_feature_page.py
from pages.base.base_page import BasePage

class MyFeaturePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.some_button = "button[data-action='my-action']"

    def click_button(self):
        self.click(self.some_button)
        self.page.wait_for_load_state("networkidle")
```

### 2. Add a test
```python
# tests/ui/my_feature/test_my_feature.py
import pytest
from pages.my_feature.my_feature_page import MyFeaturePage

@pytest.mark.smoke
def test_feature_works(login):
    page = login
    feature = MyFeaturePage(page)
    feature.click_button()
    assert feature.is_visible(".success-message"), "Expected success message"
```

### 3. Run it
```bash
pytest tests/ui/my_feature/test_my_feature.py -v
```

---

## Files Never Committed to Git

```
.env                  ← credentials and secrets
venv/                 ← virtual environment
__pycache__/          ← Python bytecode cache
.pytest_cache/        ← pytest internal cache
allure-results/       ← raw Allure data
allure-report/        ← generated HTML report
screenshots/          ← failure screenshots
report.html           ← pytest-html report
```

---

## Contact

QA Lead: dilip.ale@renegadeinsurance.com
