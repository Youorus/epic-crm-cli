"""
ViewSet pour la gestion des contrats dans le CRM.

Règles d'accès :
    - GESTION  : accès complet à tous les contrats.
    - COMMERCIAL : accès uniquement aux contrats liés à ses propres clients.
    - SUPPORT : lecture seule (selon la règle métier actuelle).

Fonctionnalités :
    - CRUD complet selon permissions.
    - Filtrage avancé via `django-filter` sur plusieurs champs :
        * is_signed : booléen (exact)
        * client : ID du client (exact)
        * sales_contact : ID du commercial (exact)
        * amount_due / total_amount : filtres numériques (exact, gt, gte, lt, lte)
        * created_at : filtres de date (exact, gte, lte)
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from crm.contracts.models import Contract
from crm.contracts.permissions import ContractPermission
from crm.contracts.serializers import ContractSerializer


class ContractViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal pour la gestion des contrats.

    - GESTION :
        Accès complet à tous les contrats (lecture/écriture/suppression).
    - COMMERCIAL :
        Lecture et écriture uniquement sur les contrats de ses propres clients.
    - SUPPORT :
        Lecture seule (pas de création ni modification).
    """
    serializer_class = ContractSerializer
    permission_classes = [ContractPermission]
    filter_backends = [DjangoFilterBackend]

    # Champs disponibles pour le filtrage via paramètres de requête
    # Exemple : ?is_signed=true&amount_due__gt=0&client=1
    filterset_fields = {
        "is_signed": ["exact"],
        "client": ["exact"],
        "sales_contact": ["exact"],
        "amount_due": ["exact", "gt", "gte", "lt", "lte"],
        "total_amount": ["exact", "gt", "gte", "lt", "lte"],
        "created_at": ["exact", "gte", "lte"],
        # Ajouter "updated_at" si un filtrage sur les mises à jour est nécessaire
    }

    def get_queryset(self):
        """
        Retourne le queryset adapté au rôle de l'utilisateur connecté.
        """
        user = self.request.user

        if user.role == "GESTION":
            # Accès à tous les contrats
            return Contract.objects.all()

        if user.role == "COMMERCIAL":
            # Accès uniquement aux contrats liés à ses propres clients
            return Contract.objects.filter(client__sales_contact=user)

        if user.role == "SUPPORT":
            # Accès en lecture seule à tous les contrats
            return Contract.objects.all()

        # Aucun accès pour les rôles non reconnus
        return Contract.objects.none()