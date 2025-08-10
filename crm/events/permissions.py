# crm/events/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class EventPermission(BasePermission):
    """
    COMMERCIAL : peut créer un événement (contrat signé) pour ses clients.
    GESTION    : accès complet (CRUD).
    SUPPORT    : lecture + modification (PUT/PATCH) uniquement de ses événements.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role in ["GESTION", "COMMERCIAL"]:
            return True

        if user.role == "SUPPORT":
            # Autoriser lecture ET update (PUT/PATCH). Pas de POST/DELETE.
            if request.method in SAFE_METHODS:
                return True
            if request.method in ("PUT", "PATCH"):
                return True
            return False

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == "GESTION":
            return True

        if request.method in SAFE_METHODS:
            # COMMERCIAL/SUPPORT peuvent lire ce que leur get_queryset expose
            # (déjà filtré par la view), mais on reste prudent :
            if user.role == "COMMERCIAL":
                return obj.client.sales_contact_id == user.id
            if user.role == "SUPPORT":
                return obj.support_contact_id == user.id
            return False

        if user.role == "COMMERCIAL":
            # Commercial n’édite pas l’événement (selon ta règle actuelle)
            return False

        if user.role == "SUPPORT":
            # Support peut modifier uniquement ses événements
            return obj.support_contact_id == user.id and request.method in ("PUT", "PATCH")

        return False