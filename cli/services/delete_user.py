import requests

from cli.utils.config import USER_URL


def delete_user(token: str, user_id: str):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.delete(f"{USER_URL}{user_id}/", headers=headers)
        if response.status_code == 204:
            print("✅ Collaborateur supprimé avec succès.")
        elif response.status_code == 404:
            print("❌ Utilisateur introuvable.")
        else:
            print("❌ Erreur lors de la suppression :", response.json())
    except requests.exceptions.RequestException:
        print("❌ Erreur de connexion au serveur.")