"""Permissions personnalisées pour le modèle Client.

Ce module définit les règles d'accès aux objets Client selon le rôle de
l'utilisateur :
    - GESTION : accès complet en lecture/écriture/suppression (CRUD complet)
    - COMMERCIAL :
        * Lecture seule (SAFE_METHODS) pour tous les clients
        * Création (POST) autorisée
        * Modification (PUT/PATCH) autorisée uniquement sur ses propres clients
        * Suppression interdite
    - SUPPORT :
        * Lecture seule (SAFE_METHODS)
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class ClientPermission(BasePermission):
    """Implémente les règles d'accès au modèle Client selon le rôle utilisateur."""

    def has_permission(self, request, view):
        """Vérifie les permissions globales selon la méthode HTTP et le rôle."""
        user = request.user

        # Refuser si utilisateur non authentifié
        if not user or not user.is_authenticated:
            return False

        # Rôle GESTION → accès complet
        if user.role == "GESTION":
            return True

        # Rôle COMMERCIAL
        if user.role == "COMMERCIAL":
            # Lecture autorisée
            if request.method in SAFE_METHODS:
                return True
            # Création autorisée
            if request.method == "POST":
                return True
            # PUT/PATCH seront filtrés au niveau objet
            if request.method in ("PUT", "PATCH"):
                return True
            # Suppression interdite
            return False

        # Rôle SUPPORT → lecture seule
        if user.role == "SUPPORT":
            return request.method in SAFE_METHODS

        # Par défaut → refuser
        return False

    def has_object_permission(self, request, view, obj):
        """Vérifie les permissions au niveau d'un objet Client précis."""
        user = request.user

        # GESTION → accès complet
        if user.role == "GESTION":
            return True

        # Lecture seule pour tous les rôles
        if request.method in SAFE_METHODS:
            return True

        # COMMERCIAL → modification uniquement si c’est son client
        if user.role == "COMMERCIAL":
            return getattr(obj, "sales_contact_id", None) == user.id

        # SUPPORT → jamais de modification
        return False