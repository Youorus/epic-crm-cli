"""
Sérialiseurs pour le modèle Event.

Ce module définit le sérialiseur principal utilisé par l’API pour :
- convertir les instances d’Event en JSON (lecture),
- valider et désérialiser les données entrantes (création / mise à jour),
- exposer des champs « façade » en lecture seule (labels pratiques côté frontend/CLI).
"""

from rest_framework import serializers

from crm.events.models import Event


class EventSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle `Event`.

    Champs supplémentaires (read-only) exposés pour faciliter l’affichage côté client :
      - `client_full_name` : nom complet du client (via la FK `client`).
      - `contract_id` : identifiant du contrat (utile si le frontend n’exploite que l’ID).
      - `support_contact_username` : username du collaborateur support assigné (si existant).

    Remarques :
      - Les champs en lecture seule ne sont pas modifiables via l’API.
      - La cohérence métier (ex. « client correspond au contrat », « contrat signé »,
        etc.) doit être validée dans la vue/serializer (ex. `perform_create` dans le ViewSet).
    """

    # Facades en lecture seule (données dérivées des relations)
    client_full_name = serializers.CharField(
        source="client.full_name",
        read_only=True,
        help_text="Nom complet du client lié à l’événement (lecture seule).",
    )
    contract_id = serializers.IntegerField(
        source="contract.id",
        read_only=True,
        help_text="Identifiant du contrat lié (doublon pratique de `contract`).",
    )
    support_contact_username = serializers.CharField(
        source="support_contact.username",
        read_only=True,
        help_text="Nom d’utilisateur du support assigné (lecture seule).",
    )

    class Meta:
        model = Event
        fields = [
            # Identité / relations
            "id",
            "contract",
            "contract_id",
            "client",
            "client_full_name",
            "support_contact",
            "support_contact_username",
            # Données métier
            "event_name",
            "event_start",
            "event_end",
            "location",
            "attendees",
            "notes",
            # Meta
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "contract_id",
            "client_full_name",
            "support_contact_username",
        ]
        # NB : on laisse `contract`, `client`, `support_contact` modifiables selon règles
        # de permissions et validations métier définies au niveau du ViewSet/serializer.