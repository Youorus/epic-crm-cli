from cli.validators.attendees_validator import validate_attendees
from cli.validators.contract_validator import validate_contract_id
from cli.validators.exceptions import ValidationError
from cli.validators.validate_signed_contract import validate_signed_contract
from cli.validators.validate_event_dates import validate_event_dates


def create_event_form(signed_contracts, user):
    print("\n=== 🗓️ Création d’un événement ===")
    print("(Tape 'retour' à tout moment pour annuler)\n")

    if not signed_contracts:
        print("⚠️ Aucun contrat signé disponible.")
        return None

    print("📄 Contrats signés disponibles :")
    for c in signed_contracts:
        total = float(c.get('total_amount') or 0)
        due = float(c.get('amount_due') or 0)
        paid = total - due
        print(
            f"  ➤ ID: {c['id']} | Client ID: {c['client']} | "
            f"Montant: {total:.2f} € | Payé: {paid:.2f} € | "
            f"Commercial: {c.get('sales_contact')} | "
            f"Signé: {'✅' if c.get('is_signed') else '❌'}"
        )

    # Choix du contrat
    while True:
        contract_id_input = input("\n🔗 ID du contrat : ").strip()
        if contract_id_input.lower() == "retour":
            return None
        try:
            contract_id = validate_contract_id(contract_id_input, signed_contracts)
            validate_signed_contract(contract_id, signed_contracts)

            # ✅ Vérifie que l'utilisateur est bien le commercial en charge
            contract = next((c for c in signed_contracts if c['id'] == contract_id), None)
            if not contract:
                print("❌ Contrat introuvable.")
                continue

            if str(contract.get('sales_contact')) != str(user.get('id')) and str(contract.get('sales_contact')) != str(user.get('username')):
                print("❌ Vous ne pouvez créer un événement que pour vos propres contrats.")
                continue

            break
        except ValidationError as e:
            print(f"❌ {e}")

    # Nom de l'événement
    while True:
        event_name = input("📛 Nom de l'événement : ").strip()
        if event_name.lower() == "retour":
            return None
        if not event_name:
            print("❌ Le nom ne peut pas être vide.")
            continue
        break

    # Lieu
    while True:
        location = input("📍 Lieu : ").strip()
        if location.lower() == "retour":
            return None
        if not location:
            print("❌ Le lieu est requis.")
            continue
        break

    # Nombre de participants
    while True:
        attendees_input = input("👥 Nombre de participants : ").strip()
        if attendees_input.lower() == "retour":
            return None
        try:
            attendees = validate_attendees(attendees_input)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # Dates de début et de fin
    while True:
        start_input = input("🕒 Date/heure de début (ex: 29 mai 2025 à 14h) : ").strip()
        if start_input.lower() == "retour":
            return None

        end_input = input("🕓 Date/heure de fin (ex: 30 mai 2025 à 16h) : ").strip()
        if end_input.lower() == "retour":
            return None

        try:
            start_dt, end_dt = validate_event_dates(start_input, end_input)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # Notes (facultatif)
    notes = input("📝 Notes (facultatif) : ").strip()

    return {
        "contract": contract_id,
        "event_name": event_name,
        "location": location,
        "attendees": attendees,
        "event_start": start_dt.strftime("%Y-%m-%d %H:%M"),
        "event_end": end_dt.strftime("%Y-%m-%d %H:%M"),
        "notes": notes
    }