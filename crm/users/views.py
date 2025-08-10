from rest_framework import viewsets, permissions

from crm.users.models import User
from crm.users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal pour la gestion des utilisateurs.

    📌 Règles d'accès :
    - Rôle **GESTION** :
        → Accès complet en lecture et écriture (CRUD complet sur tous les utilisateurs).
    - Autres rôles :
        → Lecture seule de leur propre profil.
        → Pas de création ni de suppression.
        → Pas d'accès aux profils d'autres utilisateurs.

    🔒 La logique de permissions est centralisée dans la classe interne `IsGestionOrSelfReadOnly`.
    """
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Détermine dynamiquement les permissions en fonction de l'action demandée.
        On définit une permission interne spécifique au `UserViewSet`.
        """

        class IsGestionOrSelfReadOnly(permissions.BasePermission):
            """
            Permission personnalisée :
            - Autorise un accès total si l'utilisateur est GESTION.
            - Autorise la lecture de son propre profil pour les autres.
            - Bloque toute modification sauf pour GESTION.
            """

            def has_permission(self, request, view):
                """
                Vérifie l'autorisation d'accès globale à la vue.
                """
                # GESTION → accès complet
                if request.user.is_authenticated and request.user.role == "GESTION":
                    return True

                # Autres rôles :
                # Autorise seulement la lecture de leur propre profil
                if view.action in ["retrieve", "list"]:
                    return request.user.is_authenticated

                # Toute autre action est refusée
                return False

            def has_object_permission(self, request, view, obj):
                """
                Vérifie l'autorisation sur un objet précis (instance User).
                """
                # GESTION → accès complet
                if request.user.role == "GESTION":
                    return True

                # Autres rôles → lecture uniquement de leur propre profil
                return obj == request.user and request.method in permissions.SAFE_METHODS

        # Retourne une instance de notre permission personnalisée
        return [IsGestionOrSelfReadOnly()]

    def get_queryset(self):
        """
        Restreint la liste des utilisateurs retournée selon le rôle :
        - GESTION : tous les utilisateurs
        - Autres : uniquement eux-mêmes
        """
        user = self.request.user
        if user.role == "GESTION":
            return User.objects.all()
        return User.objects.filter(pk=user.pk)