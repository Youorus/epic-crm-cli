from django.db import models
from django.conf import settings

from crm.clients.models import Client
from crm.contracts.models import Contract


class Event(models.Model):
    """
    Modèle Event : Représente un événement lié à un contrat et un client.
    """
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='event',
        verbose_name="Contrat associé"
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name="Client concerné"
    )
    support_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        verbose_name="Contact support"
    )
    event_name = models.CharField(
        max_length=255,
        verbose_name="Nom de l'événement"
    )
    event_start = models.DateTimeField(
        verbose_name="Début de l'événement"
    )
    event_end = models.DateTimeField(
        verbose_name="Fin de l'événement"
    )
    location = models.CharField(
        max_length=500,
        verbose_name="Lieu"
    )
    attendees = models.PositiveIntegerField(
        verbose_name="Nombre de participants"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes complémentaires"
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
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ["-event_start"]

    def __str__(self):
        return f"{self.event_name} ({self.client.full_name})"

    @property
    def duration(self):
        """Retourne la durée de l'événement en minutes."""
        return int((self.event_end - self.event_start).total_seconds() // 60)