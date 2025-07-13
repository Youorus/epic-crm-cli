import requests
from cli.utils.config import EVENT_URL

def list_events(token: str, filters: str = "", user_id: int = None, display: bool = True):
    headers = {'Authorization': f'Bearer {token}'}

    # 🔧 Ajout du filtre support_contact si user_id est fourni
    if user_id:
        if '?' in filters:
            filters += f"&support_contact={user_id}"
        else:
            filters = f"?support_contact={user_id}"

    try:
        response = requests.get(EVENT_URL + filters, headers=headers)

        if response.status_code == 200:
            events = response.json()

            if not events:
                print("🔍 Aucun événement trouvé.")
                return []

            if display:
                print("\n📅 --- Liste des événements ---")
                for e in events:
                    support = e.get("support_contact") or "— Aucun support"
                    print(
                        f"\n🆔 Événement #{e['id']} : {e['event_name']}\n"
                        f"   👤 Client ID      : {e['client']}\n"
                        f"   🧑‍💼 Support        : {support}\n"
                        f"   📍 Lieu           : {e.get('location', 'Non spécifié')}\n"
                        f"   👥 Participants   : {e.get('attendees', 'NC')}\n"
                        f"   🕒 Début          : {e['event_start']}\n"
                        f"   🕓 Fin            : {e['event_end']}\n"
                        f"   📝 Notes          : {e.get('notes', 'Aucune note')}"
                    )

            return events

        else:
            print("❌ Erreur lors de la récupération des événements :")
            try:
                print(response.json())
            except ValueError:
                print(response.text)
            return []

    except requests.exceptions.RequestException as e:
        print(f"❌ Le serveur est injoignable : {e}")
        return []