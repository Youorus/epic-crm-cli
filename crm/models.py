from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    ROLE_CHOICES = [
        ('COMMERCIAL', 'Commercial'),
        ('SUPPORT', 'Support'),
        ('GESTION', 'Gestion'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Client(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=255)

    date_created = models.DateField(auto_now_add=True)
    last_contact = models.DateField()

    sales_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients'
    )

    def __str__(self):
        return f"{self.full_name} - {self.company_name}"


class Contract(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='contracts'
    )

    sales_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contracts'
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)

    date_created = models.DateField(auto_now_add=True)
    is_signed = models.BooleanField(default=False)

    def __str__(self):
        return f"Contrat #{self.id} - {self.client.full_name}"


class Event(models.Model):
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='event'
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='events'
    )

    support_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )

    event_name = models.CharField(max_length=255)
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    location = models.CharField(max_length=500)
    attendees = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.event_name} ({self.client.full_name})"