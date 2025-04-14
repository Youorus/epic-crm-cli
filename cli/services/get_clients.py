import requests
from cli.utils.config import CLIENT_URL

def list_clients(token: str, display: bool = True):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(CLIENT_URL, headers=headers)
        if response.status_code == 200:
            clients = response.json()

            if not clients:
                print("🔍 Aucun client trouvé.")
                return []

            if display:
                print("\n--- Liste des clients ---")
                for c in clients:
                    sales_contact = c.get("sales_contact_name", "Non assigné")
                    print(f"{c['id']}: {c['full_name']} - {c['company_name']} - {c['email']} (Commercial : {sales_contact})")

            return clients

        elif response.status_code == 403:
            print("⛔ Accès refusé. Vous n'avez pas la permission d'afficher les clients.")
            return []
        else:
            print("❌ Erreur lors de la récupération des clients.")
            print("📨", response.text)
            return []

    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")
        return []