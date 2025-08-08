from rest_framework.permissions import BasePermission, SAFE_METHODS

class EventPermission(BasePermission):
    """
    COMMERCIAL : Peut créer un événement (après signature du contrat) pour ses clients.
    GESTION : Peut assigner le support, tout voir/éditer.
    SUPPORT : Lecture/édition uniquement sur les événements qui lui sont assignés.
    """

    def has_permission(self, request, view):
        if request.user.role in ["GESTION", "COMMERCIAL"]:
            return True
        if request.user.role == "SUPPORT" and request.method in SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # GESTION : accès total
        if request.user.role == "GESTION":
            return True
        # COMMERCIAL : accès si c'est l'événement de son client
        if request.user.role == "COMMERCIAL":
            if obj.client.sales_contact == request.user:
                # Peut créer si le contrat est signé
                if request.method == "POST":
                    return obj.contract.is_signed
                return request.method in SAFE_METHODS
        # SUPPORT : accès uniquement aux événements qui lui sont assignés
        if request.user.role == "SUPPORT":
            return obj.support_contact == request.user and request.method in ['GET', 'PUT', 'PATCH']
        return False