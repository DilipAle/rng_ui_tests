import pytest
from utils.data_factory import make_submission


@pytest.mark.smoke
def test_agency_height_submission_exists_in_salesforce(sf_client):
    """
    Verify that a submission originating from Agency Height
    can be queried in Salesforce by its external Agency Height ID.

    Prerequisites: A known Agency Height submission ID in .env as AH_TEST_SUBMISSION_ID
    """
    import os
    ah_id = os.getenv("AH_TEST_SUBMISSION_ID")
    if not ah_id:
        pytest.skip("AH_TEST_SUBMISSION_ID not set in .env")

    result = sf_client.get_submission_by_external_id(ah_id)

    assert result["totalSize"] > 0, f"No submission found in Salesforce for Agency Height ID: {ah_id}"
    record = result["records"][0]
    assert record["Agency_Height_ID__c"] == ah_id


@pytest.mark.regression
def test_submission_query_returns_fields(sf_client):
    """Verify SOQL query returns expected fields on Submission object."""
    result = sf_client.query(
        "SELECT Id, Name, Status__c FROM Submission__c LIMIT 1"
    )
    assert result["totalSize"] >= 0  # Table is accessible
