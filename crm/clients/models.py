from django.db import models
from django.conf import settings

class Client(models.Model):
    """
    Modèle Client : Représente un client (prospect ou actif) de l'entreprise.
    """
    full_name = models.CharField(max_length=255, verbose_name="Nom complet")
    email = models.EmailField(unique=True, verbose_name="Adresse e-mail")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    company_name = models.CharField(max_length=255, verbose_name="Entreprise")
    last_contact = models.DateField(verbose_name="Dernier contact")
    sales_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='clients',
        verbose_name="Commercial en charge"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Date de mise à jour"
    )

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.company_name}"