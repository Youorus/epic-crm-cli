import requests
from cli.utils.config import GESTION_EVENT_URL

def update_support(token, event_id, data):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    url = f"{GESTION_EVENT_URL}{event_id}/"

    try:
        response = requests.put(url, json=data, headers=headers)

        if response.status_code == 200:
            print("✅ Support modifié avec succès.")
        else:
            print("❌ Erreur lors de la mise à jour de l’événement :")
            try:
                print(response.json())
            except ValueError:
                print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"❌ Le serveur est injoignable : {e}")