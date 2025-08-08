from rest_framework import serializers

from crm.events.models import Event


class EventSerializer(serializers.ModelSerializer):
    client_full_name = serializers.CharField(source='client.full_name', read_only=True)
    contract_id = serializers.IntegerField(source='contract.id', read_only=True)
    support_contact_username = serializers.CharField(
        source='support_contact.username', read_only=True
    )

    class Meta:
        model = Event
        fields = [
            'id', 'contract', 'contract_id', 'client', 'client_full_name',
            'support_contact', 'support_contact_username',
            'event_name', 'event_start', 'event_end',
            'location', 'attendees', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'contract_id', 'client_full_name', 'support_contact_username'
        ]