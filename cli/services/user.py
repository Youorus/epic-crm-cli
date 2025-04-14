# cli/services/user.py

import requests
from cli.utils.config import USER_URL

def create_user(token: str, data: dict):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.post(USER_URL, json=data, headers=headers)
        if response.status_code == 201:
            print("✅ Collaborateur créé avec succès.")
        else:
            print("❌ Erreur lors de la création :")
            for field, messages in response.json().items():
                print(f" - {field}: {messages}")
    except requests.exceptions.RequestException:
        print("❌ Erreur de connexion au serveur.")