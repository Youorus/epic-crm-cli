from rest_framework import serializers

from crm.clients.models import Client


class ClientSerializer(serializers.ModelSerializer):
    sales_contact_username = serializers.CharField(
        source='sales_contact.username',
        read_only=True
    )

    class Meta:
        model = Client
        fields = [
            'id', 'full_name', 'email', 'phone', 'company_name',
            'last_contact', 'sales_contact', 'sales_contact_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'sales_contact_username']