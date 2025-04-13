import requests

from cli.utils.config import CONTRACT_URL


def update_contract(token, contract_id, data):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.put(f"{CONTRACT_URL}{contract_id}/", json=data, headers=headers)
        if response.status_code == 200:
            print("✅ Contrat mis à jour.")
        else:
            print("❌ Erreur lors de la mise à jour :")
            print(response.json())
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")
