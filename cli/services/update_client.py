import requests

from cli.utils.config import CLIENT_URL


def update_client(token: str, client_id: str, data: dict):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.put(f"{CLIENT_URL}{client_id}/", json=data, headers=headers)
        if response.status_code == 200:
            print("✅ Client mis à jour avec succès.")
        else:
            print("❌ Erreur lors de la mise à jour du client :")
            for field, messages in response.json().items():
                print(f" - {field} : {messages}")
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")