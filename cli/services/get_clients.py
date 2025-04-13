from cli.utils.config import CLIENT_URL
import requests

def list_clients(token: str, display: bool = True):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(CLIENT_URL, headers=headers)
        if response.status_code == 200:
            clients = response.json()
            if display:
                print("\n--- Liste des clients ---")
                for c in clients:
                    print(f"{c['id']}: {c['full_name']} - {c['company_name']} - {c['email']}")
            return clients
        else:
            print("❌ Erreur lors de la récupération des clients.")
            return []
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")
        return []