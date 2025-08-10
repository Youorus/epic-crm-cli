# tests/conftest.py
"""
Fixtures Pytest partagées pour les tests du projet.

Objectifs :
- Fournir des utilisateurs par rôle (GESTION, COMMERCIAL, SUPPORT).
- Créer des clients/contrats/événements de test cohérents.
- Exposer des APIClient authentifiés par rôle.
- Éviter les avertissements Pytest en n'appliquant PAS @pytest.mark.django_db sur les fixtures.
  → On passe plutôt la fixture 'db' en paramètre quand une fixture touche la base.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from crm.clients.models import Client
from crm.contracts.models import Contract
from crm.events.models import Event

User = get_user_model()


# ==========================
#   UTILITAIRES / API CLIENTS
# ==========================

@pytest.fixture
def api_client() -> APIClient:
    """Client DRF non authentifié."""
    return APIClient()


@pytest.fixture
def client_as():
    """
    Retourne une fonction utilitaire pour obtenir un APIClient authentifié
    pour un user donné (via force_authenticate).
    """
    def _as(user: User) -> APIClient:
        c = APIClient()
        c.force_authenticate(user=user)
        return c
    return _as


# ==========================
#   UTILISATEURS
# ==========================

@pytest.fixture
def gestion_user(db) -> User:
    """Utilisateur rôle GESTION."""
    return User.objects.create_user(
        username="gestion_test",
        email="gestion@test.com",
        password="Azerty123$",
        role="GESTION",
    )


@pytest.fixture
def commercial_user(db) -> User:
    """Premier utilisateur rôle COMMERCIAL (principal dans les tests)."""
    return User.objects.create_user(
        username="commercial_test",
        email="commercial@test.com",
        password="Azerty123$",
        role="COMMERCIAL",
    )


@pytest.fixture
def commercial_user_2(db) -> User:
    """Deuxième utilisateur rôle COMMERCIAL (sert aux tests croisés)."""
    return User.objects.create_user(
        username="commercial_test_2",
        email="commercial2@test.com",
        password="Azerty123$",
        role="COMMERCIAL",
    )


@pytest.fixture
def support_user(db) -> User:
    """Utilisateur rôle SUPPORT."""
    return User.objects.create_user(
        username="support_test",
        email="support@test.com",
        password="Azerty123$",
        role="SUPPORT",
    )


# ==========================
#   CLIENTS
# ==========================

@pytest.fixture
def client_of_commercial(db, commercial_user: User) -> Client:
    """
    Client rattaché au commercial de test — utilisé dans la majorité
    des tests sur les permissions.
    """
    return Client.objects.create(
        full_name="Client Alpha",
        email="alpha@example.com",
        phone="+33600000001",
        company_name="Alpha Corp",
        last_contact=timezone.now().date(),
        sales_contact=commercial_user,
    )


@pytest.fixture
def client_of_commercial_2(db, commercial_user_2: User) -> Client:
    """
    Client rattaché au DEUXIÈME commercial — requis par certains tests
    qui comparent la visibilité/autorisation entre deux commerciaux.
    """
    return Client.objects.create(
        full_name="Client Beta",
        email="beta@example.com",
        phone="+33600000002",
        company_name="Beta Corp",
        last_contact=timezone.now().date(),
        sales_contact=commercial_user_2,
    )


@pytest.fixture
def other_client(db, gestion_user: User) -> Client:
    """
    Client non rattaché au commercial principal.
    Sert pour tester les restrictions d’accès.
    """
    return Client.objects.create(
        full_name="Client Autre",
        email="client.autre@example.com",
        phone="+33611111111",
        company_name="Globex",
        last_contact=timezone.now().date(),
        sales_contact=gestion_user,
    )


# ==========================
#   CONTRATS
# ==========================

@pytest.fixture
def unsigned_contract(db, client_of_commercial: Client, commercial_user: User) -> Contract:
    """Contrat NON signé pour tester les restrictions de création d’événement."""
    return Contract.objects.create(
        client=client_of_commercial,
        sales_contact=commercial_user,
        total_amount=2000,
        amount_due=1000,
        is_signed=False,
    )


@pytest.fixture
def signed_contract(db, client_of_commercial: Client, commercial_user: User) -> Contract:
    """Contrat SIGNÉ lié au commercial principal."""
    return Contract.objects.create(
        client=client_of_commercial,
        sales_contact=commercial_user,
        total_amount=3000,
        amount_due=500,
        is_signed=True,
    )


@pytest.fixture
def signed_contract_commercial_2(db, client_of_commercial_2: Client, commercial_user_2: User) -> Contract:
    """Contrat SIGNÉ pour le deuxième commercial."""
    return Contract.objects.create(
        client=client_of_commercial_2,
        sales_contact=commercial_user_2,
        total_amount=3500,
        amount_due=700,
        is_signed=True,
    )


@pytest.fixture
def unsigned_contract_commercial_2(db, client_of_commercial_2: Client, commercial_user_2: User) -> Contract:
    """Contrat NON signé pour le deuxième commercial."""
    return Contract.objects.create(
        client=client_of_commercial_2,
        sales_contact=commercial_user_2,
        total_amount=1800,
        amount_due=1800,
        is_signed=False,
    )


# ==========================
#   ÉVÉNEMENTS
# ==========================

@pytest.fixture
def event_assigned_to_support(db, signed_contract: Contract, support_user: User) -> Event:
    """Événement rattaché à un contrat signé, assigné au support."""
    now = timezone.now()
    return Event.objects.create(
        contract=signed_contract,
        client=signed_contract.client,
        support_contact=support_user,
        event_name="Salon Tech",
        event_start=now + timedelta(days=1),
        event_end=now + timedelta(days=2),
        location="Paris Expo",
        attendees=150,
        notes="Prévoir badges",
    )


# ==========================
#   API CLIENTS AUTHENTIFIÉS
# ==========================

@pytest.fixture
def api_client_gestion(db, gestion_user: User) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=gestion_user)
    return c


@pytest.fixture
def api_client_commercial(db, commercial_user: User) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=commercial_user)
    return c


@pytest.fixture
def api_client_support(db, support_user: User) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=support_user)
    return c


# ==========================
#   FABRIQUE UTILISATEUR
# ==========================

@pytest.fixture
def user_factory(db):
    """
    Fabrique minimaliste pour créer un utilisateur avec un rôle donné.
    Usage : user_factory(username="x", role="COMMERCIAL")
    """
    def _make(username: str, role: str = "COMMERCIAL", email: str | None = None, password: str = "Azerty123$") -> User:
        return User.objects.create_user(
            username=username,
            email=email or f"{username}@example.com",
            password=password,
            role=role,
        )
    return _make