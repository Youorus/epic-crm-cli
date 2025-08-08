from rest_framework.permissions import BasePermission, SAFE_METHODS

class ClientPermission(BasePermission):
    """
    COMMERCIAL: CRUD sur ses clients + lecture de tous les clients.
    GESTION: Tout accès.
    SUPPORT: Lecture seule.
    """

    def has_permission(self, request, view):
        # Tous peuvent voir la liste des clients (GET)
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        # COMMERCIAL peut créer (POST)
        if request.user.role == "COMMERCIAL" and request.method == "POST":
            return True
        # GESTION peut tout faire
        if request.user.role == "GESTION":
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # GESTION : accès total
        if request.user.role == "GESTION":
            return True
        # COMMERCIAL : accès si c'est son client
        if request.user.role == "COMMERCIAL":
            if request.method in SAFE_METHODS:
                return True
            return obj.sales_contact == request.user
        # SUPPORT : lecture seule
        if request.user.role == "SUPPORT" and request.method in SAFE_METHODS:
            return True
        return False