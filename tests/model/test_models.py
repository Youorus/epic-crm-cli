# tests/test_models.py
import pytest
from django.utils import timezone
from datetime import timedelta

@pytest.mark.django_db
def test_client_str(client_of_commercial):
    """__str__ d’un client doit être lisible."""
    s = str(client_of_commercial)
    assert "Client Alpha" in s and "Alpha Corp" in s

@pytest.mark.django_db
def test_contract_str(signed_contract):
    """__str__ d’un contrat mentionne l’ID et le client."""
    s = str(signed_contract)
    assert f"Contrat #{signed_contract.id}" in s
    assert signed_contract.client.full_name in s

@pytest.mark.django_db
def test_event_duration(signed_contract):
    """duration (minutes) = event_end - event_start."""
    start = timezone.now()
    end = start + timedelta(hours=2, minutes=30)
    ev = signed_contract.event if hasattr(signed_contract, "event") else None
    if ev:
        ev.delete()
    from crm.events.models import Event
    e = Event.objects.create(
        contract=signed_contract,
        client=signed_contract.client,
        event_name="Durée test",
        event_start=start,
        event_end=end,
        location="Salle B",
        attendees=10,
    )
    assert e.duration == 150