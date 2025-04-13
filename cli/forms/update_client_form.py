from datetime import datetime

from cli.validators.email_validator import validate_email
from cli.validators.exceptions import ValidationError
from cli.validators.phone_validator import validate_phone


def update_client_form():
    print("\n=== Modification d’un client ===")
    client_id = input("ID du client à modifier : ").strip()
    data = {}

    full_name = input("Nom complet : ").strip()
    data["full_name"] = full_name

    while True:
        email = input("Email : ").strip()
        try:
            validate_email(email)
            data["email"] = email
            break
        except ValidationError as e:
            print(f"❌ {e}")

    while True:
        phone = input("Téléphone : ").strip()
        try:
            validate_phone(phone)
            data["phone"] = phone
            break
        except ValidationError as e:
            print(f"❌ {e}")

    company_name = input("Entreprise : ").strip()
    data["company_name"] = company_name

    while True:
        last_contact = input("Dernier contact (YYYY-MM-DD) : ").strip()
        try:
            # ici on suppose un format ISO, contrairement à la création
            datetime.fromisoformat(last_contact)  # validation simple
            data["last_contact"] = last_contact
            break
        except ValueError:
            print("❌ Date invalide. Format attendu : YYYY-MM-DD")

    return client_id, data