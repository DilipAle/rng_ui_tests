import pytest
from utils.data_factory import make_account


@pytest.mark.smoke
def test_create_account(sf_client):
    """Verify a new account can be created in Salesforce."""
    data = make_account()
    result = sf_client.create_account(data)
    account_id = result.get("id")

    assert account_id, "Account creation failed — no ID returned"

    # Cleanup
    sf_client.delete_account(account_id)


@pytest.mark.smoke
def test_get_account(sf_client):
    """Verify an account can be fetched by ID."""
    # Create first
    data = make_account(Name="TEST - Get Account")
    result = sf_client.create_account(data)
    account_id = result.get("id")

    account = sf_client.get_account(account_id)

    assert account["Id"] == account_id
    assert account["Name"] == "TEST - Get Account"

    # Cleanup
    sf_client.delete_account(account_id)


@pytest.mark.regression
def test_update_account(sf_client):
    """Verify an account can be updated in Salesforce."""
    data = make_account()
    result = sf_client.create_account(data)
    account_id = result.get("id")

    sf_client.update_account(account_id, {"Phone": "555-000-9999"})
    updated = sf_client.get_account(account_id)

    assert updated["Phone"] == "555-000-9999"

    # Cleanup
    sf_client.delete_account(account_id)
