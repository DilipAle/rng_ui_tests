"""
clients/salesforce_client.py — Salesforce API Tests
=====================================================
Wrapper around the simple-salesforce library that provides
clean methods for interacting with Salesforce objects via REST API.

Authentication:
    Uses username + password + security token authentication.
    Credentials are loaded from .env via SalesforceConfig.

Supported operations:
    Account  → get, create, update, delete
    Policy   → query by ID (custom object: Policy__c)
    Submission → query by Agency Height external ID (custom object: Submission__c)
    Generic  → run any raw SOQL query

Custom Salesforce objects used:
    Policy__c       → custom policy records
    Submission__c   → submissions synced from Agency Height
        Agency_Height_ID__c → external ID field linking to Agency Height

All test data created by these methods should be cleaned up in the same test
using delete_account() or equivalent — do not leave test data in Salesforce.
"""

from simple_salesforce import Salesforce
from config.config import SalesforceConfig


class SalesforceClient:
    """
    Authenticated Salesforce REST API client.

    Wraps simple-salesforce to provide clean, readable methods
    for all test operations against Salesforce objects.

    Usage (via sf_client fixture in conftest.py):
        def test_create_account(sf_client):
            result = sf_client.create_account({"Name": "Test Company"})
            account_id = result["id"]
            sf_client.delete_account(account_id)  # always clean up

        def test_query(sf_client):
            result = sf_client.query("SELECT Id, Name FROM Account LIMIT 5")
            for record in result["records"]:
                print(record["Name"])
    """

    def __init__(self):
        """
        Authenticate to Salesforce using credentials from .env.

        Raises:
            SalesforceAuthenticationFailed: If credentials are invalid
            ValueError: If required .env variables are missing
        """
        cfg = SalesforceConfig()
        self.sf = Salesforce(
            username=cfg.USERNAME,
            password=cfg.PASSWORD,
            security_token=cfg.SECURITY_TOKEN,
            domain=cfg.DOMAIN,  # 'test' for sandbox, 'login' for production
        )

    def get_account(self, account_id: str) -> dict:
        """
        Fetch a Salesforce Account record by its ID.

        Args:
            account_id: Salesforce Account record ID (18-char string)

        Returns:
            dict: Account record with all standard fields

        Example:
            account = sf_client.get_account("001Hn00000XXXXXXX")
            print(account["Name"])
        """
        return self.sf.Account.get(account_id)

    def create_account(self, data: dict) -> dict:
        """
        Create a new Account record in Salesforce.

        Args:
            data: Dict of field name → value pairs.
                  Use data_factory.make_account() to generate test data.

        Returns:
            dict: Response containing 'id' of the created record

        Example:
            result = sf_client.create_account({"Name": "Test Co", "Phone": "555-0000"})
            account_id = result["id"]
        """
        return self.sf.Account.create(data)

    def update_account(self, account_id: str, data: dict):
        """
        Update fields on an existing Account record.

        Args:
            account_id: Salesforce Account record ID
            data:       Dict of fields to update

        Example:
            sf_client.update_account("001Hn00000XXXXXXX", {"Phone": "555-9999"})
        """
        return self.sf.Account.update(account_id, data)

    def delete_account(self, account_id: str):
        """
        Delete an Account record from Salesforce.

        Always call this in test cleanup to avoid leaving test data behind.

        Args:
            account_id: Salesforce Account record ID to delete

        Example:
            sf_client.delete_account(account_id)
        """
        return self.sf.Account.delete(account_id)

    def query(self, soql: str) -> dict:
        """
        Execute a raw SOQL query and return the results.

        Args:
            soql: SOQL query string

        Returns:
            dict: Response with 'totalSize' (int) and 'records' (list of dicts)

        Example:
            result = sf_client.query("SELECT Id, Name FROM Account LIMIT 10")
            print(result["totalSize"])
            for record in result["records"]:
                print(record["Name"])
        """
        return self.sf.query(soql)

    def get_policy(self, policy_id: str) -> dict:
        """
        Query a Policy__c custom object record by its Salesforce ID.

        Args:
            policy_id: Salesforce ID of the Policy__c record

        Returns:
            dict: SOQL result with Id, Name, Status__c fields

        Example:
            result = sf_client.get_policy("a01Hn00000XXXXXXX")
            print(result["records"][0]["Status__c"])
        """
        return self.sf.query(
            f"SELECT Id, Name, Status__c FROM Policy__c WHERE Id = '{policy_id}'"
        )

    def get_submission_by_external_id(self, external_id: str) -> dict:
        """
        Find a Submission__c record by its Agency Height external ID.

        Used to verify that submissions created in Agency Height
        are correctly synced into Salesforce.

        Args:
            external_id: The Agency Height submission ID (e.g. "AH-A1B2C3D4")
                         Set AH_TEST_SUBMISSION_ID in .env for smoke test.

        Returns:
            dict: SOQL result with totalSize and records list.
                  totalSize > 0 means the sync was successful.

        Example:
            result = sf_client.get_submission_by_external_id("AH-A1B2C3D4")
            assert result["totalSize"] > 0
            print(result["records"][0]["Status__c"])
        """
        return self.sf.query(
            f"SELECT Id, Name, Status__c, Agency_Height_ID__c FROM Submission__c "
            f"WHERE Agency_Height_ID__c = '{external_id}'"
        )
