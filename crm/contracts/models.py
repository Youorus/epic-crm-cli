from django.db import models
from django.conf import settings

from crm.clients.models import Client


class Contract(models.Model):
    """
    Modèle de données pour un **contrat commercial** lié à un client.

    Champs principaux :
    - client (FK) : client propriétaire du contrat.
    - sales_contact (FK utilisateur) : commercial responsable (facultatif).
    - total_amount (Decimal) : montant total du contrat en euros.
    - amount_due (Decimal) : montant restant dû en euros.
    - is_signed (Bool) : indicateur de signature du contrat.
    - created_at / updated_at (DateTime) : horodatage de création / mise à jour.

    Remarques :
    - `on_delete=models.CASCADE` sur `client`: si le client est supprimé, les contrats associés
      sont également supprimés (comportement logique côté métier).
    - `sales_contact` est nullable : un contrat peut exister sans commercial assigné.
    - Les montants sont stockés en `Decimal` (précision financière).
    - L’ordre par défaut est du plus récent au plus ancien (`-created_at`).
    """

    # --- Relations ---
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,         # Supprime les contrats si le client est supprimé
        related_name='contracts',         # Accès inverse : client.contracts.all()
        verbose_name="Client",
    )

    sales_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,        # Si l'utilisateur est supprimé, conserver le contrat (contact = NULL)
        null=True,
        blank=True,
        related_name='contracts',         # Accès inverse : user.contracts.all()
        verbose_name="Commercial en charge",
    )

    # --- Données financières ---
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Montant total (€)",
        # Bonnes pratiques : validations métier à gérer côté serializer/form (ex: >= 0)
    )

    amount_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Montant restant dû (€)",
        # Doit idéalement être <= total_amount (à valider côté serializer/form)
    )

    # --- Statut ---
    is_signed = models.BooleanField(
        default=False,
        verbose_name="Signé",
    )

    # --- Horodatages ---
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de mise à jour",
    )

    class Meta:
        verbose_name = "Contrat"
        verbose_name_plural = "Contrats"
        ordering = ["-created_at"]  # Tri du plus récent au plus ancien

    def __str__(self) -> str:
        """
        Représentation lisible du contrat (utile dans l’admin/Django shell).
        """
        return f"Contrat #{self.id} - {self.client.full_name}"