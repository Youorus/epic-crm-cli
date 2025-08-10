# tests/test_clients_api.py
import pytest
from rest_framework.test import APIClient

CLIENTS_URL = "/api/clients/"

@pytest.mark.django_db
def test_commercial_can_create_client_auto_assign_sales_contact(commercial_user):
    """
    Un COMMERCIAL peut créer un client ; le backend force sales_contact à l’utilisateur courant.
    """
    client = APIClient()
    client.force_authenticate(user=commercial_user)

    payload = {
        "full_name": "Nouveau Client",
        "email": "nouveau@ex.com",
        "phone": "+3311223344",
        "company_name": "NewCo",
        "last_contact": "2025-05-20",
        # Même si on tente de forcer un autre sales_contact, la vue réécrase pour COMMERCIAL.
        "sales_contact": None,
    }
    r = client.post(CLIENTS_URL, payload, format="json")
    assert r.status_code in (200, 201)
    assert r.data["sales_contact"] == commercial_user.id

@pytest.mark.django_db
def test_commercial_can_update_only_own_clients(commercial_user, client_of_commercial, client_of_commercial_2):
    """
    COMMERCIAL peut mettre à jour ses clients, pas ceux d’un autre commercial.
    """
    api = APIClient()
    api.force_authenticate(user=commercial_user)

    # Update propre client → OK
    r1 = api.patch(f"{CLIENTS_URL}{client_of_commercial.id}/", {"phone": "+339999999"}, format="json")
    assert r1.status_code == 200

    # Update client d’un autre commercial → refus (403 ou 404 selon implémentation QS)
    r2 = api.patch(f"{CLIENTS_URL}{client_of_commercial_2.id}/", {"phone": "+338888888"}, format="json")
    assert r2.status_code in (403, 404)

@pytest.mark.django_db
def test_support_read_only(support_user, client_of_commercial):
    """
    SUPPORT : lecture seule.
    """
    api = APIClient()
    api.force_authenticate(user=support_user)

    # GET list → OK
    r_list = api.get(CLIENTS_URL)
    assert r_list.status_code == 200

    # POST → refus
    r_post = api.post(CLIENTS_URL, {"full_name": "X", "email": "x@x.com", "phone": "1", "company_name": "C", "last_contact": "2025-01-01"}, format="json")
    assert r_post.status_code in (403, 405)

@pytest.mark.django_db
def test_gestion_full_crud(gestion_user, client_of_commercial):
    """GESTION a accès complet aux clients."""
    api = APIClient()
    api.force_authenticate(user=gestion_user)

    # create
    r1 = api.post(CLIENTS_URL, {
        "full_name": "VIP",
        "email": "vip@vip.com",
        "phone": "+33777777",
        "company_name": "VIP SA",
        "last_contact": "2025-02-02",
        "sales_contact": client_of_commercial.sales_contact_id,
    }, format="json")
    assert r1.status_code in (200, 201)

    # update
    cid = r1.data["id"]
    r2 = api.patch(f"{CLIENTS_URL}{cid}/", {"company_name": "VIP Group"}, format="json")
    assert r2.status_code == 200

    # delete
    r3 = api.delete(f"{CLIENTS_URL}{cid}/")
    assert r3.status_code in (204, 200, 202)