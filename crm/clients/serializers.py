"""Sérialiseurs pour le modèle Client.

Ce module définit les classes permettant :
- de transformer les instances du modèle `Client` en représentations JSON,
- de valider les données entrantes lors des créations et mises à jour.

Bonnes pratiques :
- Exposer des champs "façades" en lecture seule (ex. `sales_contact_username`)
  pour éviter des jointures côté client.
- Marquer explicitement les champs en lecture seule dans `read_only_fields`.
"""

from rest_framework import serializers

from crm.clients.models import Client


class ClientSerializer(serializers.ModelSerializer):
    """Sérialiseur principal pour le modèle `Client`.

    Cette classe :
    - Convertit une instance `Client` en JSON exploitable par l’API.
    - Valide les données entrantes pour la création/mise à jour.
    - Expose un champ "façade" `sales_contact_username` (read-only) afin de
      retourner directement le nom d’utilisateur du commercial sans requête
      additionnelle côté client.

    Champs calculés/annotés :
        sales_contact_username (CharField, read-only) :
            Dérivé de la relation `sales_contact.username`. Non modifiable via l’API.
    """

    # Champ dérivé : nom d'utilisateur du commercial associé (lecture seule)
    sales_contact_username = serializers.CharField(
        source="sales_contact.username",
        read_only=True,
        help_text="Nom d'utilisateur du commercial en charge (lecture seule).",
    )

    class Meta:
        model = Client
        # Champs exposés par l’API (ordre explicite pour lisibilité)
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "company_name",
            "last_contact",
            "sales_contact",
            "sales_contact_username",  # façade pratique pour le front/CLI
            "created_at",
            "updated_at",
        ]
        # Verrouille les champs non modifiables via l’API
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "sales_contact_username",
        ]
        # (Optionnel) messages d’aide côté OpenAPI/Swagger si nécessaire
        extra_kwargs = {
            "sales_contact": {
                "help_text": "ID du commercial en charge (peut être forcé côté serveur selon le rôle)."
            },
            "last_contact": {
                "help_text": "Date du dernier contact (format ISO AAAA-MM-JJ)."
            },
        }