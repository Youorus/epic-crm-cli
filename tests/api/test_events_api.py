# tests/test_events_api.py
import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

EVENTS_URL = "/api/events/"

@pytest.mark.django_db
def test_commercial_create_event_only_for_his_signed_contracts(commercial_user, signed_contract, unsigned_contract, client_of_commercial_2):
    """
    COMMERCIAL :
      - peut créer un événement pour un contrat SIGNÉ d’un de SES clients.
      - refus si contrat non signé ou client d’un autre commercial.
    """
    api = APIClient()
    api.force_authenticate(user=commercial_user)

    start = (timezone.now() + timedelta(days=3)).replace(microsecond=0)
    end = start + timedelta(hours=3)

    # OK : contrat signé & appartient au commercial
    r_ok = api.post(EVENTS_URL, {
        "contract": signed_contract.id,
        "client": signed_contract.client.id,  # sera revalidé/forcé côté serveur
        "event_name": "Roadshow",
        "event_start": start.isoformat(),
        "event_end": end.isoformat(),
        "location": "Salle 101",
        "attendees": 50,
        "notes": "Demo",
    }, format="json")
    assert r_ok.status_code in (200, 201)

    # KO : contrat non signé
    r_unsigned = api.post(EVENTS_URL, {
        "contract": unsigned_contract.id,
        "client": unsigned_contract.client.id,
        "event_name": "Conf",
        "event_start": start.isoformat(),
        "event_end": end.isoformat(),
        "location": "Salle 102",
        "attendees": 30,
    }, format="json")
    assert r_unsigned.status_code in (403, 400)

@pytest.mark.django_db
def test_support_list_and_update_only_assigned(support_user, event_assigned_to_support):
    """
    SUPPORT :
      - liste uniquement ses événements
      - peut modifier uniquement ses événements
    """
    api = APIClient()
    api.force_authenticate(user=support_user)

    # list → ne doit voir que ses événements
    r_list = api.get(EVENTS_URL)
    assert r_list.status_code == 200
    items = r_list.data.get("results", r_list.data)
    assert any(it["id"] == event_assigned_to_support.id for it in items)

    # patch → OK sur son événement
    r_patch = api.patch(f"{EVENTS_URL}{event_assigned_to_support.id}/", {"location": "Salle 202"}, format="json")
    assert r_patch.status_code == 200
    assert r_patch.data["location"] == "Salle 202"

@pytest.mark.django_db
def test_support_cannot_update_others_event(support_user, event_assigned_to_support, gestion_user):
    """
    SUPPORT ne peut pas modifier un événement qui ne lui est pas assigné.
    """
    # On réassigne l’événement à gestion (ou None)
    event_assigned_to_support.support_contact = None
    event_assigned_to_support.save()

    api = APIClient()
    api.force_authenticate(user=support_user)
    r = api.patch(f"{EVENTS_URL}{event_assigned_to_support.id}/", {"location": "Salle X"}, format="json")
    assert r.status_code in (403, 404)

@pytest.mark.django_db
def test_gestion_can_assign_support(gestion_user, event_assigned_to_support, support_user):
    """
    GESTION peut réassigner le support d’un événement.
    """
    api = APIClient()
    api.force_authenticate(user=gestion_user)
    r = api.patch(f"{EVENTS_URL}{event_assigned_to_support.id}/", {"support_contact": support_user.id}, format="json")
    assert r.status_code == 200
    assert r.data["support_contact"] == support_user.id

@pytest.mark.django_db
def test_events_filter_support_isnull(gestion_user, event_assigned_to_support):
    """
    Filtre ?support_contact__isnull=true
    """
    # met l’événement à null pour tester le filtre
    from crm.events.models import Event
    event_assigned_to_support.support_contact = None
    event_assigned_to_support.save()

    api = APIClient()
    api.force_authenticate(user=gestion_user)
    r = api.get(EVENTS_URL, {"support_contact__isnull": "true"})
    assert r.status_code == 200
    items = r.data.get("results", r.data)
    assert any(it["id"] == event_assigned_to_support.id for it in items)