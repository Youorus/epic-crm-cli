import requests

from cli.utils.config import EVENT_URL, COMMERCIAL_EVENT_URL


def create_event(token, data):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.post(COMMERCIAL_EVENT_URL, json=data, headers=headers)
        if response.status_code == 201:
            print("🎉 Événement créé avec succès !")
        else:
            print("❌ Erreurs lors de la création de l’événement :")
            print(response.json())
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")