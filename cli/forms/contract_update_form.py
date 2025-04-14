from cli.validators.exceptions import ValidationError
from cli.validators.validate_amount import validate_amount
from cli.validators.validate_signed_input import validate_signed_input


def create_contract_form():
    print("\n=== Création d’un contrat ===")
    client_id = input("ID du client : ").strip()

    while True:
        total_amount = input("Montant total : ").strip()
        try:
            total_amount = validate_amount(total_amount)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    while True:
        amount_due = input("Montant dû : ").strip()
        try:
            amount_due = validate_amount(amount_due)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    while True:
        signed = input("Contrat signé ? (true/false) : ").strip()
        try:
            is_signed = validate_signed_input(signed)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    return {
        "client": int(client_id),
        "total_amount": total_amount,
        "amount_due": amount_due,
        "is_signed": is_signed
    }
