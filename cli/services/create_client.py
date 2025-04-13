# cli/utils/api.py

from cli.utils.config import CLIENT_URL
import requests

def create_client(token: str, data: dict):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.post(CLIENT_URL, json=data, headers=headers)
        if response.status_code == 201:
            print("✅ Client créé avec succès !")
        else:
            print("❌ Erreurs lors de la création :")
            for field, messages in response.json().items():
                print(f" - {field} : {messages}")
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")