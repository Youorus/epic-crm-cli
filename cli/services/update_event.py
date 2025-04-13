import requests

from cli.utils.config import EVENT_URL

def update_event(token, event_id, data):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.put(f"{EVENT_URL}{event_id}/", json=data, headers=headers)
        if response.status_code == 200:
            print("✅ Événement mis à jour avec succès.")
        else:
            print("❌ Erreur lors de la mise à jour de l’événement :")
            print(response.json())
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")