from rest_framework import viewsets, permissions

from crm.users.models import User
from crm.users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal pour les utilisateurs.
    Seuls les membres du département gestion peuvent créer/modifier/supprimer des utilisateurs.
    Les autres peuvent uniquement lire leur propre profil.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Exemple : seul GESTION peut créer/modifier des users, sinon SAFE_METHODS sur soi-même
        class IsGestionOrSelfReadOnly(permissions.BasePermission):
            def has_permission(self, request, view):
                if request.user.is_authenticated and request.user.role == "GESTION":
                    return True
                # Permet la lecture de son propre profil
                if view.action in ["retrieve", "list"]:
                    return request.user.is_authenticated
                return False

            def has_object_permission(self, request, view, obj):
                # GESTION accès total
                if request.user.role == "GESTION":
                    return True
                # Peut consulter/éditer son propre profil
                return obj == request.user and request.method in permissions.SAFE_METHODS

        return [IsGestionOrSelfReadOnly()]

    def get_queryset(self):
        user = self.request.user
        if user.role == "GESTION":
            return User.objects.all()
        # Les autres ne peuvent voir que leur propre profil
        return User.objects.filter(pk=user.pk)