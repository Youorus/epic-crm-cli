from rest_framework import serializers
from django.contrib.auth import get_user_model

# Récupère le modèle utilisateur actif défini dans settings.AUTH_USER_MODEL
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Sérialiseur principal pour la gestion des utilisateurs dans le CRM.

    - N'inclut pas le mot de passe en lecture (sécurité).
    - Permet de créer et de mettre à jour un utilisateur, avec hachage automatique du mot de passe.
    - Gère la validation minimale sur le mot de passe (8 caractères minimum).

    Champs inclus :
    - id : identifiant unique
    - username : nom d'utilisateur
    - email : adresse email
    - role : rôle métier (COMMERCIAL, SUPPORT, GESTION)
    - created_at / updated_at : dates automatiques
    - password : uniquement en écriture
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=True,
        help_text="Mot de passe (minimum 8 caractères)"
    )

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "role",
            "created_at", "updated_at", "password"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Création d'un nouvel utilisateur avec hachage sécurisé du mot de passe.

        Étapes :
        1. Retire le mot de passe du dictionnaire validé.
        2. Instancie l'utilisateur avec les autres champs.
        3. Utilise `set_password` pour hasher le mot de passe (jamais en clair).
        4. Sauvegarde l'utilisateur.
        """
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # Hachage sécurisé
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Mise à jour d'un utilisateur existant.
        - Met à jour les champs fournis.
        - Si un mot de passe est inclus, il est haché correctement.
        """
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # Hachage sécurisé
        instance.save()
        return instance