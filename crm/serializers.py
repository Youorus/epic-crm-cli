from rest_framework import serializers
from .models import User, Client, Contract, Event
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['sales_contact', 'date_created']

    def create(self, validated_data):
        # Associer automatiquement le commercial qui crée le client
        user = self.context['request'].user
        validated_data['sales_contact'] = user
        return super().create(validated_data)

    def validate_email(self, value):
        if Client.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un client avec cet email existe déjà.")
        return value

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'
        read_only_fields = ['sales_contact', 'date_created']

    def validate(self, data):
        user = self.context['request'].user
        client = data.get('client') or self.instance.client
        if client.sales_contact != user:
            raise serializers.ValidationError("Vous ne pouvez modifier que les contrats de vos propres clients.")
        return data

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['client']

    def validate(self, data):
        user = self.context['request'].user
        contract = data.get('contract')

        if not contract.is_signed:
            raise serializers.ValidationError("Impossible de créer un événement : le contrat n'est pas signé.")
        if contract.sales_contact != user:
            raise serializers.ValidationError("Vous ne pouvez créer des événements que pour vos propres clients.")

        return data

    def create(self, validated_data):
        validated_data['client'] = validated_data['contract'].client
        return super().create(validated_data)