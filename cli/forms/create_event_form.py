from cli.validators.attendees_validator import validate_attendees
from cli.validators.exceptions import ValidationError


def create_event_form(signed_contracts):
    print("\n=== Création d’un événement ===")
    print("(Tape 'retour' à tout moment pour annuler)")

    for c in signed_contracts:
        print(f"{c['id']}: Client ID {c['client']} - Montant total: {c['total_amount']}")

    contract_id = input("ID du contrat pour l'événement : ").strip()
    if contract_id.lower() == "retour":
        return None

    event_name = input("Nom de l'événement : ").strip()
    location = input("Lieu : ").strip()

    while True:
        attendees = input("Nombre de participants : ").strip()
        if attendees.lower() == "retour": return None
        try:
            attendees = validate_attendees(attendees)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    start = input("Date/heure de début (YYYY-MM-DD HH:MM) : ").strip()
    end = input("Date/heure de fin (YYYY-MM-DD HH:MM) : ").strip()
    notes = input("Notes (facultatif) : ").strip()

    return {
        "contract": int(contract_id),
        "event_name": event_name,
        "location": location,
        "attendees": attendees,
        "event_start": start,
        "event_end": end,
        "notes": notes
    }

# cli/forms/create_event_form.py

