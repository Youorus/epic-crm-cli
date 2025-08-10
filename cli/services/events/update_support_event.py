# cli/forms/update_support_event.py
from cli.utils.config import USER_URL  # ex: "/api/users/"
from cli.utils.session import session


def update_support_event():
    """
    Formulaire CLI pour attribuer un utilisateur SUPPORT à un événement.
    - Utilise la session globale (JWT auto/refresh)
    - Gère réponses paginées DRF côté /api/users/
    - Retourne (event_id, payload) ou (None, None) si annulé
    """
    print("\n" + "=" * 50)
    print("🛠️  ATTRIBUTION D’UN SUPPORT À UN ÉVÉNEMENT".center(50))
    print("=" * 50)
    print("(Tape 'retour' à tout moment pour annuler)\n")

    # Récupère la liste des utilisateurs (filtrage côté client sur role == SUPPORT)
    resp = session.get(USER_URL)  # si tu as un filtre serveur: USER_URL + "?role=SUPPORT"
    data = session.ok_json(resp)
    if data is None:
        return None, None

    if isinstance(data, dict) and "results" in data:
        users = data.get("results", [])
    else:
        users = data

    supports = [u for u in users if (u.get("role") == "SUPPORT")]
    if not supports:
        print("⚠️ Aucun utilisateur avec le rôle SUPPORT.")
        return None, None

    print("\n📋 Utilisateurs disponibles (Support) :")
    for idx, u in enumerate(supports, start=1):
        uname = u.get("username")
        email = u.get("email") or "aucun email"
        uid = u.get("id")
        print(f"  {idx}. {uname}  (id={uid}, {email})")

    # 2) Demande l’ID de l’événement
    while True:
        event_id_raw = input("\n🔢 ID de l’événement à modifier : ").strip()
        if event_id_raw.lower() == "retour":
            return None, None
        if event_id_raw.isdigit():
            event_id = int(event_id_raw)
            break
        print("❌ L’ID d’événement doit être un nombre entier.")

    # 3) Choix du support
    while True:
        choice = input("👤 Numéro du support à assigner : ").strip()
        if choice.lower() == "retour":
            return None, None
        if not choice.isdigit():
            print("❌ Saisis un numéro valide.")
            continue
        idx = int(choice)
        if not (1 <= idx <= len(supports)):
            print("❌ Choix hors plage. Reprends un numéro de la liste.")
            continue
        break

    selected_support_id = supports[idx - 1].get("id")

    # 4) Récap + confirmation
    print("\n" + "-" * 50)
    print("📋  RÉCAPITULATIF".center(50))
    print("-" * 50)
    print(f"   🆔 Événement ID : {event_id}")
    print(f"   🧑‍💼 Support ID  : {selected_support_id}")
    print("-" * 50)
    confirm = input("   Confirmer l’attribution ? (o/N) : ").strip().lower()
    if confirm != "o":
        print("   ❌ Attribution annulée.")
        return None, None

    # 5) Retourne les données prêtes pour l’appel API PATCH/PUT côté service
    return event_id, {"support_contact": selected_support_id}