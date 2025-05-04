# cli/services/update_contract.py
import requests
from cli.utils.config import GESTION_CONTRACT_URL

def update_contract(token, contract_id, data):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.put(f"{GESTION_CONTRACT_URL}{contract_id}/", json=data, headers=headers)

        if response.status_code == 200:
            print("✅ Contrat mis à jour.")
        elif response.status_code == 403:
            print("⛔ Accès refusé : vous n'avez pas les droits.")
        elif response.status_code == 404:
            print("❌ Contrat introuvable.")
        else:
            print("❌ Erreur lors de la mise à jour :")
            print(response.json())
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")