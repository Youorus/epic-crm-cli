# cli/utils/api.py
import requests
from cli.utils.config import CONTRACT_URL

def list_contracts(token: str, filters: str = "", display: bool = True):
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get(CONTRACT_URL + filters, headers=headers)

        if response.status_code == 200:
            contracts = response.json()

            if not contracts:
                print("🔍 Aucun contrat trouvé.")
                return []

            if display:
                print("\n--- Liste des contrats ---")
                for c in contracts:
                    print(
                        f"\n📝 Contrat #{c['id']}\n"
                        f"   👤 Client ID        : {c['client']}\n"
                        f"   💼 Montant total    : {c['total_amount']} €\n"
                        f"   💳 Restant dû       : {c['amount_due']} €\n"
                        f"   ✍️  Signé            : {'✅ Oui' if c['is_signed'] else '❌ Non'}\n"
                        f"   📅 Date de création : {c['date_created']}"
                    )

            return contracts

        elif response.status_code == 403:
            print("⛔ Accès interdit. Vous n'avez pas les permissions nécessaires.")
            return []

        else:
            print("❌ Erreur lors de la récupération des contrats :", response.json())
            return []

    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")
        return []