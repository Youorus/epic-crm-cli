from rest_framework import serializers

from crm.contracts.models import Contract


class ContractSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Contract.

    Rôle :
      - Convertit les instances de `Contract` en JSON et inversement.
      - Expose des champs "façades" en lecture seule pour faciliter l'affichage côté client :
          * `client_full_name` : nom complet du client lié
          * `sales_contact_username` : nom d'utilisateur du commercial en charge

    Remarque :
      - Les champs dérivés (`client_full_name`, `sales_contact_username`) sont **read_only**,
        ils ne peuvent pas être modifiés via l’API.
    """

    # Champ façade (lecture seule) : nom complet du client lié au contrat
    client_full_name = serializers.CharField(
        source='client.full_name',
        read_only=True
    )

    # Champ façade (lecture seule) : username du commercial lié au contrat
    sales_contact_username = serializers.CharField(
        source='sales_contact.username',
        read_only=True
    )

    class Meta:
        model = Contract
        fields = [
            'id',
            'client', 'client_full_name',
            'sales_contact', 'sales_contact_username',
            'total_amount', 'amount_due', 'is_signed',
            'created_at', 'updated_at',
        ]
        # Champs non éditables via l’API
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'client_full_name', 'sales_contact_username',
        ]