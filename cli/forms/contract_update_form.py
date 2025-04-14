from cli.validators.exceptions import ValidationError
from cli.validators.validate_amount import validate_amount
from cli.validators.validate_signed_input import validate_signed_input

def create_contract_form():
    print("\n=== 📝 Création d’un contrat ===")

    while True:
        client_id = input("ID du client : ").strip()
        if client_id.isdigit():
            break
        print("❌ L’ID client doit être un nombre entier.")

    # 💰 Montant total
    while True:
        total_amount = input("Montant total (€) : ").strip()
        try:
            total_amount = validate_amount(total_amount)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # 💳 Montant dû
    while True:
        amount_due = input("Montant dû (€) : ").strip()
        try:
            amount_due = validate_amount(amount_due)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # ✅ Statut de signature
    while True:
        signed = input("Contrat signé ? (oui/non) : ").strip().lower()
        if signed in ["oui", "o"]:
            is_signed = True
            break
        elif signed in ["non", "n"]:
            is_signed = False
            break
        else:
            print("❌ Réponds par 'oui' ou 'non'.")

    return {
        "client": int(client_id),
        "total_amount": total_amount,
        "amount_due": amount_due,
        "is_signed": is_signed
    }