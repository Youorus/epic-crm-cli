import requests
from cli.utils.config import USER_URL
from cli.validators.exceptions import ValidationError

def update_support_event(token):
    print("\n=== 🛠️ Attribution d’un support à un événement ===")
    print("(Tape 'retour' à tout moment pour annuler)")

    headers = {'Authorization': f'Bearer {token}'}

    # 📥 Étape 1 : récupérer les utilisateurs support
    try:
        response = requests.get(USER_URL, headers=headers)
        if response.status_code != 200:
            print("❌ Impossible de récupérer la liste des utilisateurs.")
            return None, None

        users = response.json()
        supports = [u for u in users if u.get("role") == "SUPPORT"]

        if not supports:
            print("⚠️ Aucun utilisateur avec le rôle SUPPORT.")
            return None, None

        print("\n📋 Utilisateurs disponibles (Support) :")
        for idx, s in enumerate(supports, start=1):
            print(f"{idx}. {s['username']} ({s.get('email', 'aucun email')})")

    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")
        return None, None

    # 📥 Étape 2 : demander l’ID de l’événement
    event_id = input("\n🔢 ID de l’événement à modifier : ").strip()
    if event_id.lower() == "retour":
        return None, None

    # 📥 Étape 3 : choisir un support
    while True:
        choice = input("👤 Numéro du support à assigner : ").strip()
        if choice.lower() == "retour":
            return None, None
        if not choice.isdigit() or not (1 <= int(choice) <= len(supports)):
            print("❌ Choix invalide. Entrez un numéro parmi la liste.")
            continue
        break

    selected_support = supports[int(choice) - 1]['id']  # ✅ maintenant c'est un int

    return event_id, {"support_contact": selected_support}