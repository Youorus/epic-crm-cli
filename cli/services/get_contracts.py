import requests
from cli.utils.config import CONTRACT_URL

def list_contracts(token: str, filters: str = "", display: bool = True):
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get(CONTRACT_URL + filters, headers=headers)

        if response.status_code == 200:
            contracts = response.json()

            # 🔍 Filtrage local si nécessaire
            if "is_signed=false" in filters:
                contracts = [c for c in contracts if not c.get('is_signed', False)]

            if "amount_due__gt=0" in filters:
                contracts = [
                    c for c in contracts
                    if float(c.get('amount_due') or 0) > 0
                ]

            if not contracts:
                print("🔍 Aucun contrat correspondant trouvé.")
                return []

            if display:
                print("\n--- Liste des contrats filtrés ---")
                for c in contracts:
                    try:
                        montant_total = float(c.get('total_amount') or 0)
                        montant_restant = float(c.get('amount_due') or 0)
                        montant_paye = montant_total - montant_restant
                    except (ValueError, TypeError):
                        montant_total = montant_restant = montant_paye = 0.0

                    print(
                        f"\n📝 Contrat #{c['id']}\n"
                        f"   👤 Client ID        : {c['client']}\n"
                        f"   💼 Montant total    : {montant_total:.2f} €\n"
                        f"   💶 Déjà payé         : {montant_paye:.2f} €\n"
                        f"   💳 Restant dû       : {montant_restant:.2f} €\n"
                        f"   ✍️  Signé            : {'✅ Oui' if c.get('is_signed') else '❌ Non'}\n"
                        f"   📅 Date de création : {c.get('date_created')}"
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