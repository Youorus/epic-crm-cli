from rest_framework.permissions import BasePermission, SAFE_METHODS

class ContractPermission(BasePermission):
    """
    GESTION : Peut créer/éditer tous les contrats.
    COMMERCIAL : Lecture seule sur les contrats de ses clients.
    SUPPORT : Lecture seule.
    """

    def has_permission(self, request, view):
        if request.user.role == "GESTION":
            return True
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        # GESTION : accès total
        if request.user.role == "GESTION":
            return True
        # COMMERCIAL : lecture seule si le contrat concerne son client
        if request.user.role == "COMMERCIAL" and request.method in SAFE_METHODS:
            return obj.client.sales_contact == request.user
        # SUPPORT : lecture seule
        if request.user.role == "SUPPORT" and request.method in SAFE_METHODS:
            return True
        return False