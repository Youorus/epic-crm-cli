# cli/services/get_contract_by_id.py

import requests
from cli.utils.config import CONTRACT_URL

def get_contract_by_id(contract_id: str, token: str):
    headers = {'Authorization': f'Bearer {token}'}
    url = f"{CONTRACT_URL}{contract_id}/"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 404:
            print("❌ Contrat non trouvé.")
            return None

        elif response.status_code == 403:
            print("⛔ Accès refusé au contrat.")
            return None

        else:
            print(f"❌ Erreur inattendue ({response.status_code}) : {response.text}")
            return None

    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")
        return None