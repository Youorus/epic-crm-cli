import requests
from cli.utils.config import EVENT_URL

def list_events(token: str, filters: str = "", display: bool = True):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(EVENT_URL + filters, headers=headers)
        if response.status_code == 200:
            events = response.json()

            if not events:
                print("🔍 Aucun événement trouvé.")
                return []

            if display:
                print("\n--- Liste des événements ---")
                for e in events:
                    support = e.get("support_contact", None)
                    support_display = support if support else "Aucun support"
                    print(
                        f"{e['id']} • {e['event_name']} | Client ID: {e['client']} | "
                        f"Support: {support_display} | "
                        f"Début: {e['event_start']} | Fin: {e['event_end']}"
                    )

            return events
        else:
            print("❌ Erreur lors de la récupération des événements.")
            return []
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")
        return []