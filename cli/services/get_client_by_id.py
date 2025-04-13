import requests
from cli.utils.config import CLIENT_URL

def get_client_by_id(client_id: str, token: str):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(f"{CLIENT_URL}{client_id}/", headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"❌ Aucun client trouvé avec l’ID {client_id}")
            return None
        else:
            print(f"❌ Erreur lors de la récupération du client : {response.status_code}")
            return None
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")
        return None