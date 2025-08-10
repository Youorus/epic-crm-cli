# tests/test_contracts_api.py
import pytest
from rest_framework.test import APIClient

CONTRACTS_URL = "/api/contracts/"

@pytest.mark.django_db
def test_commercial_sees_only_his_clients_contracts(commercial_user, client_of_commercial, client_of_commercial_2):
    """
    COMMERCIAL : ne liste que les contrats des clients dont il est le sales_contact.
    """
    from crm.contracts.models import Contract

    # un contrat pour chaque client
    Contract.objects.create(client=client_of_commercial, sales_contact=commercial_user,
                            total_amount=1000, amount_due=1000, is_signed=False)
    Contract.objects.create(client=client_of_commercial_2, sales_contact=client_of_commercial_2.sales_contact,
                            total_amount=2000, amount_due=0, is_signed=True)

    api = APIClient()
    api.force_authenticate(user=commercial_user)
    r = api.get(CONTRACTS_URL)
    assert r.status_code == 200
    ids = [row["client"] for row in r.data.get("results", r.data)]
    assert client_of_commercial.id in ids
    assert client_of_commercial_2.id not in ids

@pytest.mark.django_db
def test_contract_filters(gestion_user, signed_contract, unsigned_contract):
    """
    Filtres via django-filter : ?is_signed=true / ?amount_due__gt=0
    """
    api = APIClient()
    api.force_authenticate(user=gestion_user)

    r1 = api.get(CONTRACTS_URL, {"is_signed": "true"})
    assert r1.status_code == 200
    items = r1.data.get("results", r1.data)
    assert any(it["id"] == signed_contract.id for it in items)

    r2 = api.get(CONTRACTS_URL, {"amount_due__gt": "0"})
    assert r2.status_code == 200
    items2 = r2.data.get("results", r2.data)
    assert any(it["id"] == unsigned_contract.id for it in items2)

@pytest.mark.django_db
def test_commercial_cannot_update_contract(commercial_user, signed_contract):
    """
    Selon ContractPermission : COMMERCIAL = lecture seule.
    """
    api = APIClient()
    api.force_authenticate(user=commercial_user)
    r = api.patch(f"{CONTRACTS_URL}{signed_contract.id}/", {"amount_due": 0}, format="json")
    assert r.status_code in (403, 405)