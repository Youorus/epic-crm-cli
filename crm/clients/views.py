# crm/clients/views.py
"""
Ce module définit le ViewSet `ClientViewSet` pour la gestion des clients dans l'application CRM.

Règles métier :
---------------
- **GESTION** : CRUD complet sur tous les clients.
- **COMMERCIAL** :
    * list / retrieve : accès à tous les clients.
    * create : crée des clients et devient automatiquement leur `sales_contact`.
    * update / partial_update : uniquement ses propres clients.
    * delete : interdit (géré par les permissions).
- **SUPPORT** : accès en lecture seule à tous les clients.

Les permissions sont gérées par `ClientPermission` et certaines sécurités
supplémentaires sont appliquées directement dans `perform_create` et `perform_update`.
"""

from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from crm.clients.models import Client
from crm.clients.permissions import ClientPermission
from crm.clients.serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des clients.

    Fournit toutes les actions CRUD, avec filtrage et restrictions selon le rôle :
    - GESTION : CRUD complet
    - COMMERCIAL : lecture de tous les clients, modification uniquement des siens
    - SUPPORT : lecture seule
    """
    serializer_class = ClientSerializer
    permission_classes = [ClientPermission]

    def get_queryset(self):
        """
        Retourne le queryset adapté au rôle de l'utilisateur connecté.
        Optimise les requêtes avec `select_related` pour inclure le `sales_contact`.

        - GESTION : accès à tous les clients.
        - COMMERCIAL :
            * list/retrieve → tous les clients
            * autres actions → uniquement ses propres clients
        - SUPPORT : lecture seule de tous les clients
        - Utilisateur non authentifié ou rôle inconnu → aucun résultat
        """
        user = self.request.user
        qs = Client.objects.select_related("sales_contact")

        if not user.is_authenticated:
            return Client.objects.none()

        if user.role == "GESTION":
            return qs

        if user.role == "COMMERCIAL":
            if self.action in ("list", "retrieve"):
                return qs
            return qs.filter(sales_contact=user)

        if user.role == "SUPPORT":
            return qs

        return Client.objects.none()

    def perform_create(self, serializer):
        """
        Lors de la création :
        - Si l'utilisateur est COMMERCIAL → forcer `sales_contact` = utilisateur connecté
          (sécurité côté serveur, ignore toute valeur envoyée par le client).
        - Autres rôles → création normale.
        """
        user = self.request.user
        if user.role == "COMMERCIAL":
            serializer.save(sales_contact=user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        """
        Lors de la modification :
        - COMMERCIAL :
            * Vérifie que le client lui appartient, sinon PermissionDenied.
            * Empêche toute réassignation du `sales_contact`.
        - GESTION : modification complète possible.
        """
        user = self.request.user
        instance = self.get_object()

        if user.role == "COMMERCIAL":
            if instance.sales_contact_id != user.id:
                # Défense en profondeur (en plus des filtres/permissions)
                raise PermissionDenied("Vous ne pouvez modifier que vos propres clients.")
            serializer.save(sales_contact=instance.sales_contact)
        else:
            serializer.save()