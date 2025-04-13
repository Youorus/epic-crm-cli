import requests
import re

from cli.validators import (
    validate_username,
    validate_email,
    validate_password,
    validate_role,
    ValidationError,
)

API_BASE_URL = "http://127.0.0.1:8000/api/"
USER_URL = API_BASE_URL + "users/"

def gestion_menu(token):
    while True:
        print("\n--- Menu GESTION ---")
        print("1. Lister les utilisateurs")
        print("2. Créer un contrat")
        print("3. Associer support à un événement")
        print("4. Créer un collaborateur")
        print("0. Quitter")
        choice = input("Choix : ")

        if choice == '1':
            list_users(token)
        elif choice == '2':
            create_contract(token)
        elif choice == '3':
            assign_support(token)
        elif choice == '4':
            create_user(token)
        elif choice == '0':
            break
        else:
            print("❌ Choix invalide.")

def list_users(token):
    print("\n--- Liste des utilisateurs ---")
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(USER_URL, headers=headers)
        if response.status_code == 200:
            users = response.json()
            for user in users:
                print(f"{user['id']}: {user['username']} - {user['email']} - {user['role']}")
        else:
            print("❌ Erreur lors de la récupération des utilisateurs.")
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")

def create_user(token):
    print("\n=== Création d’un nouveau collaborateur ===")
    print("(Tape 'retour' à tout moment pour revenir au menu)\n")

    while True:
        try:
            username = input("Nom d'utilisateur : ").strip()
            if username.lower() == 'retour':
                return
            validate_username(username)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    while True:
        try:
            email = input("Email : ").strip()
            if email.lower() == 'retour':
                return
            validate_email(email)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    while True:
        try:
            password = input("Mot de passe (min. 8 caractères) : ").strip()
            if password.lower() == 'retour':
                return
            validate_password(password)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    while True:
        try:
            role = input("Rôle (COMMERCIAL / SUPPORT / GESTION) : ").strip().upper()
            if role.lower() == 'retour':
                return
            validate_role(role)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    data = {
        "username": username,
        "email": email,
        "password": password,
        "role": role
    }

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(USER_URL, json=data, headers=headers)
        if response.status_code == 201:
            created_user = response.json()
            print("\n🎉 Utilisateur créé avec succès !")
            print("🧑 Nom :", created_user.get("username"))
            print("📧 Email :", created_user.get("email"))
            print("👔 Rôle :", created_user.get("role"))
        else:
            print("❌ Erreur lors de la création du collaborateur :")
            errors = response.json()
            for field, messages in errors.items():
                if isinstance(messages, list):
                    print(f" - {field}: {', '.join(str(m) for m in messages)}")
                else:
                    print(f" - {field}: {messages}")
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")

def create_contract(token):
    print("🛠️ Fonction de création de contrat à implémenter.")

def assign_support(token):
    print("🛠️ Fonction d’association de support à un événement à implémenter.")