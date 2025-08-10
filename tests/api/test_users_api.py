# tests/test_users_api.py
import pytest
from rest_framework.test import APIClient

USERS_URL = "/api/users/"

@pytest.mark.django_db
def test_gestion_can_create_user(gestion_user):
    """GESTION peut créer un utilisateur."""
    api = APIClient()
    api.force_authenticate(user=gestion_user)
    r = api.post(USERS_URL, {
        "username": "nouveau_user",
        "email": "n@ex.com",
        "role": "SUPPORT",
        "password": "Passw0rd!",
    }, format="json")
    assert r.status_code in (200, 201)

@pytest.mark.django_db
def test_non_gestion_cannot_create_user(commercial_user):
    """Un non-GESTION ne peut pas créer d’utilisateur."""
    api = APIClient()
    api.force_authenticate(user=commercial_user)
    r = api.post(USERS_URL, {
        "username": "x",
        "email": "x@ex.com",
        "role": "SUPPORT",
        "password": "Passw0rd!",
    }, format="json")
    assert r.status_code in (403, 405)

@pytest.mark.django_db
def test_user_can_retrieve_self(commercial_user):
    """Un utilisateur peut consulter son propre profil (via la vue filtrée)."""
    api = APIClient()
    api.force_authenticate(user=commercial_user)
    r = api.get(USERS_URL)
    assert r.status_code == 200
    items = r.data.get("results", r.data)
    assert any(it["username"] == commercial_user.username for it in items)