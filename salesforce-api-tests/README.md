# Salesforce API Tests

REST API tests for the **Renegade Insurance Salesforce** org.
No browser — tests call the Salesforce API directly via `simple-salesforce`.

Tests cover Account CRUD operations and cross-system submission verification
(confirming that Agency Height submissions are correctly synced into Salesforce).

---

## Project Structure

```
salesforce-api-tests/
│
├── .env                          # Credentials — NEVER commit this file
├── pytest.ini                    # Test runner config
├── requirements.txt              # All Python dependencies
├── conftest.py                   # sf_client + sf_config fixtures
│
├── config/
│   └── config.py                 # SalesforceConfig — loads .env credentials
│
├── clients/
│   └── salesforce_client.py     # Salesforce API wrapper (Account, Policy, Submission)
│
├── utils/
│   └── data_factory.py          # Faker-based test data generators
│
└── tests/
    ├── account/
    │   └── test_account_api.py        # 3 tests: create, get, update
    └── submission/
        └── test_submission_api.py     # 2 tests: cross-system sync, SOQL query
```

---

## Setup

```bash
# 1. Navigate to this project
cd salesforce-api-tests

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies (no Playwright needed)
pip install -r requirements.txt

# 4. Create .env file
touch .env
```

---

## .env Variables

```env
ENV=qa

QA_SF_USERNAME=your_username@renegadeinsurance.com.qa
QA_SF_PASSWORD=yourpassword
QA_SF_SECURITY_TOKEN=yourSecurityToken
QA_SF_DOMAIN=test                        # 'test' for sandbox | 'login' for production

# Optional — for cross-system submission test
AH_TEST_SUBMISSION_ID=AH-XXXXXXXX
```

### How to get your Salesforce Security Token
```
Salesforce → My Settings → Personal → Reset My Security Token
```
A new token will be emailed to your Salesforce account email address.

---

## Running Tests

```bash
source venv/bin/activate

# Smoke tests
pytest -m smoke -v

# All tests
pytest -v

# API tests only
pytest -m api -v

# Specific file
pytest tests/account/test_account_api.py -v
```

---

## Test Suite

### Account API Tests (`tests/account/test_account_api.py`)

| Test | Marker | Description |
|---|---|---|
| `test_create_account` | smoke | Create account → verify ID returned → delete |
| `test_get_account` | smoke | Create account → fetch by ID → verify fields → delete |
| `test_update_account` | regression | Create → update phone → verify updated value → delete |

### Submission API Tests (`tests/submission/test_submission_api.py`)

| Test | Marker | Description |
|---|---|---|
| `test_agency_height_submission_exists_in_salesforce` | smoke | Verify Agency Height submission is synced into Salesforce (requires `AH_TEST_SUBMISSION_ID` in .env) |
| `test_submission_query_returns_fields` | regression | Verify Submission__c object is accessible via SOQL |

---

## Test Data

All test data is generated using `utils/data_factory.py` with the `Faker` library.
Each test run generates unique data — no hardcoded values.

```python
from utils.data_factory import make_account, make_submission

# Generate fake account data
data = make_account()
# {"Name": "Smith LLC", "Phone": "555-0123", "BillingCity": "Austin", ...}

# Override specific fields
data = make_account(Name="TEST - My Scenario", Phone="555-0000")

# Generate fake submission data
sub = make_submission()
# {"Name": "TEST-SUBMISSION-A1B2C3D4", "Agency_Height_ID__c": "AH-E5F6G7H8"}
```

**Always clean up test data:**
```python
result = sf_client.create_account(data)
account_id = result["id"]

# ... your assertions ...

sf_client.delete_account(account_id)  # never skip this
```

---

## SalesforceClient Methods

| Method | Description |
|---|---|
| `get_account(id)` | Fetch account by Salesforce ID |
| `create_account(data)` | Create new account, returns `{"id": "..."}` |
| `update_account(id, data)` | Update fields on existing account |
| `delete_account(id)` | Delete account (use in test cleanup) |
| `query(soql)` | Run any SOQL query |
| `get_policy(id)` | Query Policy__c by ID |
| `get_submission_by_external_id(ah_id)` | Query Submission__c by Agency Height ID |

---

## Writing New Tests

```python
import pytest
from utils.data_factory import make_account

@pytest.mark.smoke
def test_my_api_test(sf_client):
    # 1. Generate test data
    data = make_account(Name="TEST - My Test")

    # 2. Create in Salesforce
    result = sf_client.create_account(data)
    account_id = result["id"]

    # 3. Assert
    assert account_id, "No ID returned"
    account = sf_client.get_account(account_id)
    assert account["Name"] == "TEST - My Test"

    # 4. Always clean up
    sf_client.delete_account(account_id)
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
pytest==9.0.2
pytest-xdist==3.6.1
pytest-rerunfailures==14.0
pytest-html==4.2.0
pytest-metadata==3.1.1
allure-pytest==2.13.5
requests==2.32.3
simple-salesforce==1.12.6
python-dotenv==1.1.0
faker==24.0.0
```
