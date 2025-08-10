"""Modèles liés aux clients.

Ce module définit le modèle `Client`, qui représente un prospect ou un client
actif de l’entreprise. Il inclut des informations d’identification, des
coordonnées, un rattachement à un commercial, ainsi que des horodatages de
création et de mise à jour.
"""

from django.db import models
from django.conf import settings


class Client(models.Model):
    """Représente un client (prospect ou actif) de l'entreprise.

    Champs principaux :
        - full_name : nom complet du contact côté client.
        - email : adresse e-mail unique (sert aussi d’identifiant fonctionnel).
        - phone : numéro de téléphone (normalisé côté sérialiseur/CLI si besoin).
        - company_name : raison sociale de l’entreprise du client.
        - last_contact : date du dernier échange (utile pour le suivi commercial).
        - sales_contact : utilisateur (commercial) en charge de ce client.

    Champs techniques :
        - created_at : date/heure de création (définie automatiquement).
        - updated_at : date/heure de dernière mise à jour (mise à jour auto).
    """

    # ——— Identité & coordonnées ———
    full_name = models.CharField(
        max_length=255,
        verbose_name="Nom complet",
        help_text="Nom et prénom de l’interlocuteur principal."
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Adresse e-mail",
        help_text="Adresse e-mail unique du client."
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Téléphone",
        help_text="Numéro de téléphone du client (format libre)."
    )
    company_name = models.CharField(
        max_length=255,
        verbose_name="Entreprise",
        help_text="Nom de l’entreprise (raison sociale)."
    )

    # ——— Suivi commercial ———
    last_contact = models.DateField(
        verbose_name="Dernier contact",
        help_text="Date du dernier échange avec ce client."
    )
    sales_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clients",
        verbose_name="Commercial en charge",
        help_text="Collaborateur (rôle COMMERCIAL) responsable de ce client."
    )

    # ——— Horodatage ———
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        help_text="Créé automatiquement à l’insertion."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de mise à jour",
        help_text="Mise à jour automatique à chaque modification."
    )

    class Meta:
        # Libellés d’administration et tri par défaut (du plus récent au plus ancien).
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Retourne une représentation lisible du client (nom + entreprise)."""
        return f"{self.full_name} - {self.company_name}"