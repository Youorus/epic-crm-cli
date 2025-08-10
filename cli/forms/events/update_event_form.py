import dateparser
from typing import Optional

from cli.utils.config import EVENT_URL
from cli.utils.session import session
from cli.validators.attendees_validator import validate_attendees
from cli.validators.exceptions import ValidationError
from cli.validators.validate_event_dates import validate_event_dates


def format_french_date(date_str: str) -> str:
    """
    Convertit une date ISO (ex.: '2025-05-20T15:00:00+02:00') vers un format lisible FR :
    '20 mai 2025 à 15:00'. En cas d’échec, retourne la chaîne d’origine.
    """
    dt = dateparser.parse(date_str, languages=["fr"])
    if not dt:
        return date_str
    return dt.strftime("%d %B %Y à %H:%M")


def update_event_form(token: Optional[str] = None, user: Optional[dict] = None):
    """
    Formulaire CLI : modification d’un événement (retourne (event_id, data)).
    - Utilise la session globale (JWT déjà géré).
    - Vérifie que l’utilisateur SUPPORT ne modifie que ses propres événements.
    - Respecte l’existant : si l’utilisateur laisse un champ vide, on conserve la valeur actuelle.
    - Pour les dates : si une des deux est modifiée, on valide le couple (début/fin) ensemble.

    Args:
        token: conservé pour compatibilité, non utilisé (on passe par `session`).
        user:  dict utilisateur ; si absent, on prend `session.user`.

    Returns:
        tuple(event_id: str, payload: dict) | (None, None)
    """
    print("\n=== ✏️ Modification d’un événement ===")

    # ——————————————————————————————————————————————————————————————
    # Saisie de l’ID événement
    # ——————————————————————————————————————————————————————————————
    event_id = input("ID de l'événement à modifier : ").strip()
    if not event_id.isdigit():
        print("❌ L’ID d’événement doit être un entier.")
        return None, None

    # ——————————————————————————————————————————————————————————————
    # Récupération de l’événement via l’API
    # ——————————————————————————————————————————————————————————————
    resp = session.get(f"{EVENT_URL}{event_id}/")
    if resp.status_code != 200:
        if resp.status_code == 404:
            print("❌ Événement introuvable.")
        else:
            try:
                print(f"❌ Erreur ({resp.status_code}) :", resp.json())
            except ValueError:
                print(f"❌ Erreur ({resp.status_code}) :", resp.text)
        return None, None

    event = resp.json()

    # ——————————————————————————————————————————————————————————————
    # Contrôle d’autorisation côté CLI (défense en profondeur)
    # ——————————————————————————————————————————————————————————————
    current_user = user or (session.user or {})
    current_role = current_user.get("role")
    current_user_id = current_user.get("id")
    current_username = current_user.get("username")

    # Le serializer expose en général:
    #   - support_contact (ID) et/ou
    #   - support_contact_username (username)
    ev_support_id = event.get("support_contact")
    ev_support_username = event.get("support_contact_username")

    if current_role == "SUPPORT":
        # Un support ne peut modifier QUE ses propres événements.
        is_owner_by_id = (ev_support_id is not None and ev_support_id == current_user_id)
        is_owner_by_username = (ev_support_username is not None and ev_support_username == current_username)
        if not (is_owner_by_id or is_owner_by_username):
            print("⛔ Vous ne pouvez modifier que les événements qui vous sont assignés.")
            return None, None

    print("➡️ Appuie sur Entrée pour conserver la valeur actuelle.")
    payload = {}

    # ——————————————————————————————————————————————————————————————
    # 📛 Nom de l'événement
    # ——————————————————————————————————————————————————————————————
    event_name_in = input(f"Nom [{event.get('event_name', '')}] : ").strip()
    payload["event_name"] = event_name_in or event.get("event_name", "")

    # ——————————————————————————————————————————————————————————————
    # 📍 Lieu
    # ——————————————————————————————————————————————————————————————
    location_in = input(f"Lieu [{event.get('location', '')}] : ").strip()
    payload["location"] = location_in or event.get("location", "")

    # ——————————————————————————————————————————————————————————————
    # 👥 Nombre de participants (validation forte)
    # ——————————————————————————————————————————————————————————————
    while True:
        attendees_in = input(f"Participants [{event.get('attendees', '')}] : ").strip()
        if not attendees_in:
            payload["attendees"] = event.get("attendees")
            break
        try:
            payload["attendees"] = validate_attendees(attendees_in)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # ——————————————————————————————————————————————————————————————
    # 🕒 Début / 🕓 Fin
    # Règle : si l’un des deux champs est saisi, on revalide le couple.
    # On accepte des entrées FR (ex: "18 avril 2025 à 14h") ; si vide, on reprend
    # la valeur existante mais transformée en FR pour le validateur.
    # ——————————————————————————————————————————————————————————————
    start_display = format_french_date(event["event_start"])
    end_display = format_french_date(event["event_end"])

    start_input = input(f"Début [{start_display}] (ex: 29 mai 2025 à 18h) : ").strip()
    end_input = input(f"Fin   [{end_display}] (ex: 30 mai 2025 à 20h) : ").strip()

    # Si aucune saisie : on conserve l’ISO tel quel (pas de revalidation inutile)
    if not start_input and not end_input:
        payload["event_start"] = event["event_start"]
        payload["event_end"] = event["event_end"]
    else:
        # On combine : valeur saisie OU valeur existante transformée en français
        start_src = start_input or start_display
        end_src = end_input or end_display
        try:
            start_dt, end_dt = validate_event_dates(start_src, end_src)
            payload["event_start"] = start_dt.strftime("%Y-%m-%d %H:%M")
            payload["event_end"] = end_dt.strftime("%Y-%m-%d %H:%M")
        except ValidationError as e:
            print(f"❌ {e}")
            return None, None

    # ——————————————————————————————————————————————————————————————
    # 📝 Notes
    # ——————————————————————————————————————————————————————————————
    notes_in = input(f"Notes [{event.get('notes', 'Aucune')}] : ").strip()
    payload["notes"] = notes_in if notes_in else event.get("notes", "")

    # ——————————————————————————————————————————————————————————————
    # Champs requis par ton backend (cohérence immuable contrat/client)
    # ——————————————————————————————————————————————————————————————
    # On renvoie les valeurs existantes pour éviter toute tentative de mutation.
    payload["client"] = event["client"]
    payload["contract"] = event["contract"]

    return event_id, payload