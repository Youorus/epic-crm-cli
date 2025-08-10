# tests/test_serializers.py
import pytest
from crm.clients.serializers import ClientSerializer
from crm.contracts.serializers import ContractSerializer
from crm.events.serializers import EventSerializer

@pytest.mark.django_db
def test_client_serializer_exposes_sales_username(client_of_commercial):
    """Le serializer Client expose bien sales_contact_username en lecture seule."""
    data = ClientSerializer(client_of_commercial).data
    assert data["sales_contact_username"] == client_of_commercial.sales_contact.username

@pytest.mark.django_db
def test_contract_serializer_exposes_client_full_name(signed_contract):
    """Le serializer Contract expose client_full_name & sales_contact_username."""
    data = ContractSerializer(signed_contract).data
    assert data["client_full_name"] == signed_contract.client.full_name
    assert data["sales_contact_username"] == signed_contract.sales_contact.username

@pytest.mark.django_db
def test_event_serializer_exposes_readonly_fields(event_assigned_to_support):
    """Le serializer Event expose client_full_name, contract_id, support_contact_username."""
    data = EventSerializer(event_assigned_to_support).data
    assert data["client_full_name"] == event_assigned_to_support.client.full_name
    assert data["contract_id"] == event_assigned_to_support.contract.id
    assert data["support_contact_username"] == event_assigned_to_support.support_contact.username