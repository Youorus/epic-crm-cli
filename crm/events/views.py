# crm/events/views.py
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from crm.events.models import Event
from crm.events.permissions import EventPermission
from crm.events.serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    Gestion des événements avec filtrage par rôle.

    - GESTION :
        * CRUD complet sur tous les événements.
    - COMMERCIAL :
        * list/retrieve : uniquement les événements liés à ses clients (client.sales_contact = lui)
        * create        : uniquement pour ses clients (client déduit du contrat)
        * update        : normalement interdit sauf règles spécifiques.
    - SUPPORT :
        * list/retrieve : uniquement ses événements assignés (support_contact = lui)
        * update        : uniquement ses événements (notes, horaires, etc.).
    """
    serializer_class = EventSerializer
    permission_classes = [EventPermission]

    def get_queryset(self):
        """Filtrage automatique selon le rôle de l'utilisateur."""
        user = self.request.user
        qs = Event.objects.select_related("contract", "client", "support_contact")

        if not user.is_authenticated:
            return Event.objects.none()

        if user.role == "GESTION":
            return qs

        if user.role == "COMMERCIAL":
            return qs.filter(client__sales_contact=user)

        if user.role == "SUPPORT":
            return qs.filter(support_contact=user)

        return Event.objects.none()

    filterset_fields = {
        "support_contact": ["exact", "isnull"],  # ?support_contact=3 | ?support_contact__isnull=true
        "client": ["exact"],  # ?client=5
        "event_start": ["gte", "lte"],  # ?event_start__gte=2025-08-01
    }
    ordering_fields = ["event_start", "event_end", "created_at"]
    search_fields = ["event_name", "location", "client__full_name"]

    def perform_create(self, serializer):
        user = self.request.user
        contract = serializer.validated_data.get("contract")
        if not contract:
            raise PermissionDenied("Contrat requis pour créer un événement.")

        client = contract.client

        # 💡 défense en profondeur : cohérence client/contrat
        if serializer.validated_data.get("client") and serializer.validated_data["client"].id != client.id:
            raise PermissionDenied("Le client ne correspond pas au contrat fourni.")

        # 🚫 Contrat non signé => pas d'événement
        if not contract.is_signed:
            raise PermissionDenied("Impossible de créer un événement pour un contrat non signé.")

        # 👤 Règle métier : un COMMERCIAL ne crée que pour ses clients
        if user.role == "COMMERCIAL" and client.sales_contact_id != user.id:
            raise PermissionDenied("Vous ne pouvez créer un événement que pour vos propres clients.")

        serializer.save(client=client)

    def perform_update(self, serializer):
        """
        - Empêche changement de contrat/client après création.
        - Vérifie qu'un SUPPORT ne met à jour que ses propres événements.
        """
        user = self.request.user
        instance = self.get_object()
        data = serializer.validated_data

        # Interdire modification du contrat
        if "contract" in data and data["contract"] != instance.contract:
            raise PermissionDenied("Le contrat d’un événement ne peut pas être modifié.")

        # Interdire modification du client
        if "client" in data and data["client"] != instance.client:
            raise PermissionDenied("Le client d’un événement ne peut pas être modifié.")

        # SUPPORT → ne peut modifier que ses événements
        if user.role == "SUPPORT" and instance.support_contact_id != user.id:
            raise PermissionDenied("Vous ne pouvez modifier que vos propres événements.")

        serializer.save()