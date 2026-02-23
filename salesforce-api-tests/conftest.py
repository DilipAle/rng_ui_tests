"""
conftest.py — Salesforce API Tests
=====================================
Pytest configuration for Salesforce REST API tests.
No browser is used in this project — tests call the Salesforce API directly.

Fixtures defined here:
    sf_client → authenticated SalesforceClient instance (session-scoped)
    sf_config → raw SalesforceConfig values (session-scoped)

Required .env file (place in salesforce-api-tests/):
    ENV=qa
    QA_SF_USERNAME=your_sf_username
    QA_SF_PASSWORD=your_sf_password
    QA_SF_SECURITY_TOKEN=your_security_token
    QA_SF_DOMAIN=test                   # 'test' for sandbox, 'login' for production
    AH_TEST_SUBMISSION_ID=AH-XXXXXXXX   # optional, for cross-system submission test

How to get your Salesforce Security Token:
    Salesforce → My Settings → Personal → Reset My Security Token
    A new token will be emailed to your Salesforce account email.
"""

import pytest
from clients.salesforce_client import SalesforceClient
from config.config import SalesforceConfig


@pytest.fixture(scope="session")
def sf_client():
    """
    Create and return an authenticated Salesforce API client.

    Scope: session — one connection is made and reused across all tests.
    Authenticates using credentials from .env via SalesforceConfig.

    Returns:
        SalesforceClient: Authenticated client with methods for Account,
                          Policy, Submission, and raw SOQL queries.

    Usage in tests:
        def test_create_account(sf_client):
            result = sf_client.create_account({"Name": "Test Co"})
            assert result["id"]
    """
    return SalesforceClient()


@pytest.fixture(scope="session")
def sf_config():
    """
    Return the raw Salesforce configuration values.

    Scope: session — loaded once per session.

    Returns:
        SalesforceConfig: Config object with USERNAME, PASSWORD,
                          SECURITY_TOKEN, DOMAIN, ENV attributes.

    Usage in tests:
        def test_something(sf_config):
            print(sf_config.ENV)
            print(sf_config.DOMAIN)
    """
    return SalesforceConfig()
