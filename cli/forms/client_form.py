from cli.validators.date_parser import parse_french_date
from cli.validators.email_validator import validate_email
from cli.validators.exceptions import ValidationError
from cli.validators.phone_validator import validate_phone


def create_client_form():
    print("\n=== Création d’un client ===")
    data = {}

    while True:
        full_name = input("Nom complet : ").strip()
        if full_name:
            data["full_name"] = full_name
            break
        print("❌ Le nom complet est requis.")

    while True:
        email = input("Email : ").strip()
        try:
            validate_email(email)
            data["email"] = email
            break
        except ValidationError as e:
            print(f"❌ {e}")

    while True:
        default_prefix = "+33 "
        phone = input(f"Téléphone [{default_prefix}]: ").strip()
        if not phone.startswith("+33"):
            phone = default_prefix + phone
        try:
            validate_phone(phone)
            data["phone"] = phone
            break
        except ValidationError as e:
            print(f"❌ {e}")

    while True:
        company = input("Nom de l'entreprise : ").strip()
        if company:
            data["company_name"] = company
            break
        print("❌ Le nom de l’entreprise est requis.")

    while True:
        last_contact_str = input("Dernier contact (ex: 29 mars 2023) : ").strip()
        try:
            data["last_contact"] = str(parse_french_date(last_contact_str))
            break
        except ValidationError as e:
            print(f"❌ {e}")

    return data


def update_client_form():
    print("\n=== Modification d’un client ===")
    client_id = input("ID du client à modifier : ").strip()

    full_name = input("Nom complet : ").strip()
    email = input("Email : ").strip()
    phone = input("Téléphone : ").strip()
    company_name = input("Entreprise : ").strip()
    last_contact = input("Dernier contact (YYYY-MM-DD) : ").strip()

    data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "company_name": company_name,
        "last_contact": last_contact
    }

    return client_id, data