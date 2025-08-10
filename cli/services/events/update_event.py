# cli/menus/support_menu.py
from cli.services.events.get_events import list_events
from cli.utils.session import session
from cli.utils.config import EVENT_URL


def _input_int(prompt: str) -> int | None:
    raw = input(prompt).strip()
    if raw.lower() == "retour":
        return None
    if raw.isdigit():
        return int(raw)
    print("❌ L’ID doit être un entier.")
    return None


def _update_event_form_support(event_id: int) -> dict | None:
    """
    Formulaire simple pour mettre à jour un événement
    (support peut éditer par ex. nom, lieu, horaires, notes — selon tes permissions).
    On laisse le backend refuser si le support n’est pas responsable.
    """
    print("\n=== ✏️  Modification de l’événement ===")
    print("(Entrée vide pour conserver la valeur — 'retour' pour annuler)")

    # On récupère l’état actuel pour montrer des valeurs (facultatif : tu peux le faire si ton API retourne le détail)
    # Ici on PATCH en mode “champs saisis uniquement”.

    payload = {}

    name = input("📛 Nouveau nom (optionnel) : ").strip()
    if name.lower() == "retour":
        return None
    if name:
        payload["event_name"] = name

    location = input("📍 Nouveau lieu (optionnel) : ").strip()
    if location.lower() == "retour":
        return None
    if location:
        payload["location"] = location

    attendees = input("👥 Participants (optionnel) : ").strip()
    if attendees.lower() == "retour":
        return None
    if attendees:
        if attendees.isdigit() and int(attendees) >= 0:
            payload["attendees"] = int(attendees)
        else:
            print("❌ Nombre de participants invalide. Ignoré.")

    # Dates (format ISO local si tu veux, sinon laisse tel quel selon tes validateurs)
    start = input("🕒 Début (YYYY-MM-DD HH:MM, optionnel) : ").strip()
    if start.lower() == "retour":
        return None
    if start:
        payload["event_start"] = start

    end = input("🕓 Fin (YYYY-MM-DD HH:MM, optionnel) : ").strip()
    if end.lower() == "retour":
        return None
    if end:
        payload["event_end"] = end

    notes = input("📝 Notes (optionnel) : ").strip()
    if notes.lower() == "retour":
        return None
    if notes:
        payload["notes"] = notes

    if not payload:
        print("ℹ️ Aucun changement saisi.")
        return None
    return payload


