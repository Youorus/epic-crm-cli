from cli.services.get_contract_by_id import get_contract_by_id
from cli.validators.exceptions import ValidationError
from cli.validators.validate_amount import validate_amount

def update_contract_form(token, user):
    print("\n=== Modification d’un contrat ===")
    contract_id = input("ID du contrat à modifier : ").strip()

    # 🔁 Récupération du contrat existant
    contract = get_contract_by_id(contract_id, token)

    if not contract:
        print("❌ Contrat introuvable.")
        return None, None

    # ✅ Vérification des permissions
    if contract["sales_contact"] != user["id"]:
        print("⛔ Vous ne pouvez modifier que vos propres contrats.")
        return None, None

    print("➡️ Laisse vide pour conserver la valeur actuelle.")
    data = {}

    # 💰 Montant total
    while True:
        total_amount = input(f"Montant total [{contract['total_amount']}] : ").strip()
        if not total_amount:
            data["total_amount"] = contract["total_amount"]
            break
        try:
            data["total_amount"] = validate_amount(total_amount)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # 💳 Montant dû
    while True:
        amount_due = input(f"Montant dû [{contract['amount_due']}] : ").strip()
        if not amount_due:
            data["amount_due"] = contract["amount_due"]
            break
        try:
            data["amount_due"] = validate_amount(amount_due)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # ✅ Statut signé
    while True:
        is_signed = input(f"Contrat signé ? (oui/non) [{'oui' if contract['is_signed'] else 'non'}] : ").strip().lower()
        if not is_signed:
            data["is_signed"] = contract["is_signed"]
            break
        if is_signed in ["oui", "o"]:
            data["is_signed"] = True
            break
        elif is_signed in ["non", "n"]:
            data["is_signed"] = False
            break
        else:
            print("❌ Réponds par 'oui' ou 'non'.")

    # ✅ Inclure le client (obligatoire pour PUT)
    data["client"] = contract["client"]

    return contract_id, data