from cli.validators.attendees_validator import validate_attendees
from cli.validators.exceptions import ValidationError


def update_event_form():
    print("\n=== Modification d’un événement ===")
    event_id = input("ID de l'événement à modifier : ").strip()

    event_name = input("Nom de l'événement : ").strip()
    location = input("Lieu : ").strip()

    while True:
        attendees = input("Nombre de participants : ").strip()
        try:
            attendees = validate_attendees(attendees)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    start = input("Date/heure de début (YYYY-MM-DD HH:MM) : ").strip()
    end = input("Date/heure de fin (YYYY-MM-DD HH:MM) : ").strip()
    notes = input("Notes (facultatif) : ").strip()

    data = {
        "event_name": event_name,
        "location": location,
        "attendees": attendees,
        "event_start": start,
        "event_end": end,
        "notes": notes
    }

    return event_id, data