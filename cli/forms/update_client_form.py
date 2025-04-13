from datetime import datetime

from cli.services.get_client_by_id import get_client_by_id
from cli.validators.email_validator import validate_email
from cli.validators.exceptions import ValidationError
from cli.validators.phone_validator import validate_phone


def update_client_form(token, user):
    print("\n=== Modification d’un client ===")
    client_id = input("ID du client à modifier : ").strip()

    client = get_client_by_id(client_id, token)

    if not client:
        print("❌ Client introuvable.")
        return None, None

    # ✅ Vérifier si l'utilisateur est autorisé à modifier ce client
    if client["sales_contact"] != user["id"]:
        print("⛔ Vous ne pouvez modifier que les clients dont vous êtes responsable.")
        return None, None

    print("➡️ Laisse vide pour conserver la valeur actuelle.")

    data = {}

    # Nom complet
    full_name = input(f"Nom complet [{client['full_name']}] : ").strip()
    data["full_name"] = full_name if full_name else client["full_name"]

    # Email
    while True:
        email = input(f"Email [{client['email']}] : ").strip()
        email = email if email else client["email"]
        try:
            validate_email(email)
            data["email"] = email
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # Téléphone
    while True:
        default = client["phone"]
        phone = input(f"Téléphone [{default}] : ").strip()
        phone = phone if phone else default
        try:
            validate_phone(phone)
            data["phone"] = phone
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # Entreprise
    company_name = input(f"Entreprise [{client['company_name']}] : ").strip()
    data["company_name"] = company_name if company_name else client["company_name"]

    # Dernier contact
    while True:
        last_contact = input(f"Dernier contact [{client['last_contact']}] (YYYY-MM-DD) : ").strip()
        last_contact = last_contact if last_contact else client["last_contact"]
        try:
            datetime.fromisoformat(last_contact)
            data["last_contact"] = last_contact
            break
        except ValueError:
            print("❌ Date invalide. Format attendu : YYYY-MM-DD")

    return client_id, data