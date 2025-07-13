import requests
import dateparser
from cli.utils.config import EVENT_URL
from cli.validators.attendees_validator import validate_attendees
from cli.validators.exceptions import ValidationError
from cli.validators.validate_event_dates import validate_event_dates


def format_french_date(date_str: str) -> str:
    """
    Transforme une date ISO comme '2025-05-20T15:00:00+02:00'
    en format lisible : '20 mai 2025 à 15:00'
    """
    dt = dateparser.parse(date_str, languages=["fr"])
    if not dt:
        return date_str  # fallback
    return dt.strftime("%d %B %Y à %H:%M")


def update_event_form(token, user):
    print("\n=== ✏️ Modification d’un événement ===")
    event_id = input("ID de l'événement à modifier : ").strip()
    headers = {'Authorization': f'Bearer {token}'}

    # 🔍 Récupération de l'événement
    try:
        response = requests.get(f"{EVENT_URL}{event_id}/", headers=headers)
        if response.status_code != 200:
            print("❌ Événement introuvable.")
            return None, None
        event = response.json()
    except requests.RequestException:
        print("❌ Le serveur est injoignable.")
        return None, None

    # 🔐 Vérification des permissions
    if event.get("support_contact") != user["username"]:
        print("⛔ Vous ne pouvez modifier que les événements qui vous sont assignés.")
        return None, None

    print("➡️ Appuie sur Entrée pour conserver la valeur actuelle.")
    data = {}

    # 📛 Nom de l'événement
    event_name = input(f"Nom [{event['event_name']}] : ").strip()
    data["event_name"] = event_name if event_name else event["event_name"]

    # 📍 Lieu
    location = input(f"Lieu [{event['location']}] : ").strip()
    data["location"] = location if location else event["location"]

    # 👥 Nombre de participants
    while True:
        attendees = input(f"Participants [{event['attendees']}] : ").strip()
        if not attendees:
            data["attendees"] = event["attendees"]
            break
        try:
            data["attendees"] = validate_attendees(attendees)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # 🕒 Dates
    while True:
        start_display = format_french_date(event['event_start'])
        end_display = format_french_date(event['event_end'])

        start_input = input(f"Début [{start_display}] (ex: 29 mai 2025 à 18h) : ").strip()
        end_input = input(f"Fin   [{end_display}] (ex: 30 mai 2025 à 20h) : ").strip()

        # Valeur brute ISO si champ vide
        start_str = start_input if start_input else event["event_start"]
        end_str = end_input if end_input else event["event_end"]

        try:
            start_dt, end_dt = validate_event_dates(start_str, end_str)
            data["event_start"] = start_dt.strftime("%Y-%m-%d %H:%M")
            data["event_end"] = end_dt.strftime("%Y-%m-%d %H:%M")
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # 📝 Notes
    notes = input(f"Notes [{event.get('notes', 'Aucune')}] : ").strip()
    data["notes"] = notes if notes else event.get("notes", "")

    # Champs obligatoires pour la mise à jour
    data["client"] = event["client"]
    data["contract"] = event["contract"]

    return event_id, data