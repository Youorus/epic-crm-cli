import requests

from cli.utils.config import CONTRACT_URL


def create_contract(token, data):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.post(CONTRACT_URL, json=data, headers=headers)
        if response.status_code == 201:
            print("✅ Contrat créé avec succès.")
        else:
            print("❌ Erreurs lors de la création :")
            print(response.json())
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")