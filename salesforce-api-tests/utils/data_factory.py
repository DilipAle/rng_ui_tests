"""
utils/data_factory.py — Salesforce API Tests
==============================================
Generates realistic fake test data for Salesforce API tests using the Faker library.

Purpose:
    - Avoids hardcoded test data in test files
    - Each test run uses unique data (no ID collisions)
    - Supports field overrides for specific test scenarios

Usage pattern:
    1. Generate data:     data = make_account()
    2. Create in SF:      result = sf_client.create_account(data)
    3. Assert:            assert result["id"]
    4. Clean up:          sf_client.delete_account(result["id"])

Always delete records created by these factories at the end of each test.
Do not leave test data in Salesforce — it pollutes reports and search results.
"""

from faker import Faker

# Single Faker instance reused across all factory functions
fake = Faker()


def make_account(**overrides) -> dict:
    """
    Generate a realistic Salesforce Account payload with fake data.

    All fields use US-locale fake data. Any field can be overridden
    by passing it as a keyword argument.

    Args:
        **overrides: Any Salesforce Account field to override.
                     Overrides are merged after defaults are set.

    Returns:
        dict: Account field data ready to pass to sf_client.create_account()

    Examples:
        # Basic usage — all random data
        data = make_account()

        # Override specific fields
        data = make_account(Name="TEST - My Company", Phone="555-0000")

        # Override for a specific test scenario
        data = make_account(Name="TEST - Get Account")
        result = sf_client.create_account(data)
        account = sf_client.get_account(result["id"])
        assert account["Name"] == "TEST - Get Account"
    """
    data = {
        "Name": fake.company(),
        "Phone": fake.phone_number(),
        "BillingStreet": fake.street_address(),
        "BillingCity": fake.city(),
        "BillingState": fake.state_abbr(),
        "BillingPostalCode": fake.zipcode(),
        "BillingCountry": "US",
    }
    # Apply any field overrides on top of the defaults
    data.update(overrides)
    return data


def make_submission(**overrides) -> dict:
    """
    Generate a fake Salesforce Submission__c record payload.

    Creates a unique submission name and Agency Height external ID
    using UUID fragments to ensure no collisions between test runs.

    Args:
        **overrides: Any Submission__c field to override.

    Returns:
        dict: Submission field data ready to pass to sf_client.query() or create()

    Examples:
        # Basic usage
        data = make_submission()

        # Override the Agency Height ID for a specific cross-system test
        data = make_submission(Agency_Height_ID__c="AH-KNOWN123")

    Field notes:
        Name                 → "TEST-SUBMISSION-XXXXXXXX" (unique per run)
        Agency_Height_ID__c  → "AH-XXXXXXXX" (external ID from Agency Height system)
    """
    data = {
        "Name": f"TEST-SUBMISSION-{fake.uuid4()[:8].upper()}",
        "Agency_Height_ID__c": f"AH-{fake.uuid4()[:8].upper()}",
    }
    data.update(overrides)
    return data
