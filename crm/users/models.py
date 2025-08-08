from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserRole(models.TextChoices):
    COMMERCIAL = "COMMERCIAL", _("Commercial")
    SUPPORT = "SUPPORT", _("Support")
    GESTION = "GESTION", _("Gestion")

class User(AbstractUser):
    """
    Utilisateur personnalisé minimaliste mais extensible.
    Inhérente à AbstractUser : username, email, password, first_name, last_name, etc.
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

    # Optionnel : force l’unicité de l’email pour plus de sécurité (sinon laisse Django gérer)
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'role']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"