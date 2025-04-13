# cli/utils/api.py
import requests
from cli.utils.config import CONTRACT_URL

def list_contracts(token: str, filters: str = "", display: bool = True):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(CONTRACT_URL + filters, headers=headers)
        if response.status_code == 200:
            contrats = response.json()
            if display:
                print("\n--- Liste des contrats ---")
                for c in contrats:
                    print(
                        f"Contrat {c['id']} | "
                        f"Client ID: {c['client']} | "
                        f"Signé: {'✅' if c['is_signed'] else '❌'} | "
                        f"Restant dû: {c['amount_due']}€"
                    )
            return contrats
        else:
            print("❌ Erreur :", response.json())
            return []
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")
        return []