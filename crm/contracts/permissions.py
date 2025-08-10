from rest_framework.permissions import BasePermission, SAFE_METHODS


class ContractPermission(BasePermission):
    """
    Classe de permissions pour la gestion des contrats.

    Règles d'accès :
    - **GESTION** : accès complet (création, modification, suppression, lecture).
    - **COMMERCIAL** : lecture seule sur les contrats liés à ses propres clients.
    - **SUPPORT** : lecture seule sur tous les contrats.
    """

    def has_permission(self, request, view):
        """
        Vérifie si l'utilisateur a accès à la vue (niveau global, pas spécifique à un objet).

        - GESTION : accès complet, toutes méthodes HTTP autorisées.
        - COMMERCIAL & SUPPORT : accès uniquement en lecture (méthodes sûres : GET, HEAD, OPTIONS).
        - Utilisateur non authentifié : aucun accès.
        """
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.role == "GESTION":
            return True

        if request.method in SAFE_METHODS:
            return True

        # Hors SAFE_METHODS, seul GESTION peut agir
        return False

    def has_object_permission(self, request, view, obj):
        """
        Vérifie les permissions spécifiques à un objet Contrat.

        - GESTION : accès complet à tous les contrats.
        - COMMERCIAL :
            * Lecture seule (SAFE_METHODS) uniquement si le contrat concerne un de ses clients.
        - SUPPORT :
            * Lecture seule (SAFE_METHODS) sur tous les contrats.
        """
        user = request.user

        # GESTION : accès complet
        if user.role == "GESTION":
            return True

        # COMMERCIAL : lecture seule sur ses propres clients
        if user.role == "COMMERCIAL" and request.method in SAFE_METHODS:
            return obj.client.sales_contact == user

        # SUPPORT : lecture seule sur tout
        if user.role == "SUPPORT" and request.method in SAFE_METHODS:
            return True

        # Par défaut : refus
        return False