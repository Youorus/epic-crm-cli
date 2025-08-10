from django.db import models
from django.conf import settings

from crm.clients.models import Client
from crm.contracts.models import Contract


class Event(models.Model):
    """
    Modèle Event

    Représente un événement rattaché :
      - à un contrat (relation OneToOne : un contrat ne peut avoir qu’un seul événement),
      - à un client (relation ForeignKey : un client peut avoir plusieurs événements),
      - optionnellement à un collaborateur du support (responsable opérationnel).

    Champs principaux :
      - event_name     : libellé de l’événement (obligatoire)
      - event_start    : date/heure de début
      - event_end      : date/heure de fin
      - location       : lieu de l’événement
      - attendees      : nombre de participants (entier positif)
      - notes          : remarques libres (facultatif)

    Suivi :
      - created_at / updated_at : horodatage auto (création / dernière mise à jour)
    """

    # --- Liens métiers ---
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,     # si le contrat est supprimé, l’événement l’est aussi
        related_name='event',
        verbose_name="Contrat associé",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,     # si le client est supprimé, ses événements le sont aussi
        related_name='events',
        verbose_name="Client concerné",
    )
    support_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,    # si l’utilisateur support est supprimé, conserver l’événement (valeur NULL)
        null=True,
        blank=True,
        related_name='events',
        verbose_name="Contact support",
    )

    # --- Données d’événement ---
    event_name = models.CharField(
        max_length=255,
        verbose_name="Nom de l'événement",
    )
    event_start = models.DateTimeField(
        verbose_name="Début de l'événement",
    )
    event_end = models.DateTimeField(
        verbose_name="Fin de l'événement",
    )
    location = models.CharField(
        max_length=500,
        verbose_name="Lieu",
    )
    attendees = models.PositiveIntegerField(
        verbose_name="Nombre de participants",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes complémentaires",
    )

    # --- Audit ---
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de mise à jour",
    )

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ["-event_start"]   # tri décroissant par date de début

    def __str__(self) -> str:
        """Représentation lisible de l’événement (utile dans l’admin et les logs)."""
        return f"{self.event_name} ({self.client.full_name})"

    @property
    def duration(self) -> int:
        """
        Durée de l’événement en minutes (entier).
        Hypothèse : event_end >= event_start (la validation métier se fait ailleurs).
        """
        return int((self.event_end - self.event_start).total_seconds() // 60)