from rest_framework import serializers

from crm.contracts.models import Contract


class ContractSerializer(serializers.ModelSerializer):
    client_full_name = serializers.CharField(source='client.full_name', read_only=True)
    sales_contact_username = serializers.CharField(
        source='sales_contact.username', read_only=True
    )

    class Meta:
        model = Contract
        fields = [
            'id', 'client', 'client_full_name',
            'sales_contact', 'sales_contact_username',
            'total_amount', 'amount_due', 'is_signed',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'client_full_name', 'sales_contact_username'
        ]