import requests

from cli.utils.config import USER_URL


def update_user(token: str, user_id: str, data: dict):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.put(f"{USER_URL}{user_id}/", json=data, headers=headers)
        if response.status_code == 200:
            print("✅ Collaborateur mis à jour avec succès.")
        else:
            print("❌ Erreur lors de la mise à jour :")
            errors = response.json()
            for field, messages in errors.items():
                print(f" - {field}: {messages}")
    except requests.exceptions.RequestException:
        print("❌ Erreur de connexion au serveur.")