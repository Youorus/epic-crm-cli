from django.db import models
from django.conf import settings

from crm.clients.models import Client


class Contract(models.Model):
    """
    Modèle Contract : Contrat commercial lié à un client.
    """
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='contracts',
        verbose_name="Client"
    )
    sales_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contracts',
        verbose_name="Commercial en charge"
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Montant total (€)"
    )
    amount_due = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Montant restant dû (€)"
    )
    is_signed = models.BooleanField(
        default=False,
        verbose_name="Signé"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de mise à jour"
    )

    class Meta:
        verbose_name = "Contrat"
        verbose_name_plural = "Contrats"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Contrat #{self.id} - {self.client.full_name}"