# cli/forms/user_create_form.py

from cli.validators.exceptions import ValidationError
from cli.validators.email_validator import validate_email

def create_user_form():
    print("\n=== Création d’un collaborateur ===")
    data = {}

    username = input("Nom d'utilisateur : ").strip()
    data["username"] = username

    while True:
        email = input("Email : ").strip()
        try:
            validate_email(email)
            data["email"] = email
            break
        except ValidationError as e:
            print(f"❌ {e}")

    while True:
        password = input("Mot de passe : ").strip()
        if len(password) < 8:
            print("❌ Le mot de passe doit contenir au moins 8 caractères.")
        else:
            data["password"] = password
            break

    print("Rôles disponibles : COMMERCIAL / SUPPORT / GESTION")
    while True:
        role = input("Rôle : ").strip().upper()
        if role in ["COMMERCIAL", "SUPPORT", "GESTION"]:
            data["role"] = role
            break
        else:
            print("❌ Rôle invalide. Choix : COMMERCIAL, SUPPORT, GESTION")

    return data