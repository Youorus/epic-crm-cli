from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """
    Énumération des rôles utilisateurs disponibles dans l’application.

    Utilise `TextChoices` de Django pour :
    - Centraliser la définition des rôles
    - Faciliter l’utilisation dans les modèles, formulaires et serializers
    - Offrir une traduction automatique via `gettext_lazy`
    """
    COMMERCIAL = "COMMERCIAL", _("Commercial")
    SUPPORT = "SUPPORT", _("Support")
    GESTION = "GESTION", _("Gestion")


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé pour le CRM.

    Hérite de `AbstractUser`, qui fournit déjà :
    - username, email, password
    - first_name, last_name
    - is_active, is_staff, is_superuser
    - date_joined, last_login
    - Gestion intégrée de l’authentification et des permissions

    Champs ajoutés :
    - role : rôle fonctionnel dans l’organisation (COMMERCIAL, SUPPORT, GESTION)
    - created_at : date de création de l’utilisateur
    - updated_at : date de dernière modification du profil

    Remarques :
    - `EMAIL_FIELD` et `REQUIRED_FIELDS` sont ajustés pour imposer l’email et le rôle.
    - Le modèle est extensible (on peut ajouter avatar, téléphone, etc. si besoin).
    """
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        verbose_name=_("Rôle")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de création")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Date de mise à jour")
    )

    # Force l’utilisation de l’email comme champ principal pour la communication
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "role"]

    def __str__(self):
        """Retourne une représentation lisible de l’utilisateur."""
        return f"{self.username} ({self.get_role_display()})"