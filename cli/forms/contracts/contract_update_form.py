# cli/forms/create_contract_form.py
from cli.validators.exceptions import ValidationError
from cli.validators.validate_amount import validate_amount
from cli.validators.validate_signed_input import validate_signed_input
from cli.utils.session import session
from cli.utils.config import CONTRACT_URL


def create_contract_form():
    """
    Affiche un formulaire CLI pour créer un contrat, valide chaque champ,
    puis envoie la requête de création à l’API.

    Comportement :
      - Demande l'ID client (entier).
      - Valide les montants via `validate_amount` (décimal valide).
      - Valide le statut signé via `validate_signed_input` (oui/non).
      - Affiche un récapitulatif et demande confirmation.
      - En cas de confirmation, envoie un POST vers l’API (endpoint CONTRACT_URL).

    Retour:
        dict | None: L'objet contrat renvoyé par l’API en cas de succès (2xx),
                     sinon None (annulation ou erreur HTTP).
    """
    print("\n" + "=" * 50)
    print("📝   FORMULAIRE DE CRÉATION DE CONTRAT".center(50))
    print("=" * 50 + "\n")

    # ——————————————————————————————————————————————————————————————
    # 📌 ID client (doit être un entier > 0 ; ici on vérifie seulement "isdigit")
    #     Si tu veux durcir la validation, fais-le dans le validator dédié.
    # ——————————————————————————————————————————————————————————————
    while True:
        client_id_raw = input("   🔹 ID du client         : ").strip()
        if client_id_raw.isdigit():
            client_id = int(client_id_raw)
            break
        print("   ❌ L’ID client doit être un nombre entier.")

    # ——————————————————————————————————————————————————————————————
    # 💰 Montant total (validation via validator de domaine)
    # ——————————————————————————————————————————————————————————————
    while True:
        total_amount_raw = input("   💼 Montant total (€)    : ").strip()
        try:
            total_amount = validate_amount(total_amount_raw)
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # ——————————————————————————————————————————————————————————————
    # 💳 Montant dû (idem, on s’appuie sur le validator)
    # ——————————————————————————————————————————————————————————————
    while True:
        amount_due_raw = input("   💳 Montant dû (€)       : ").strip()
        try:
            amount_due = validate_amount(amount_due_raw)
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # ——————————————————————————————————————————————————————————————
    # ✅ Statut signé (reconnaît « oui/non » via validator)
    # ——————————————————————————————————————————————————————————————
    while True:
        signed_raw = input("   ✍️  Contrat signé ? (oui/non) : ").strip().lower()
        try:
            is_signed = validate_signed_input(signed_raw)
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # ——————————————————————————————————————————————————————————————
    # 📋 Récapitulatif et confirmation
    # ——————————————————————————————————————————————————————————————
    print("\n" + "-" * 50)
    print("📋   RÉCAPITULATIF DU CONTRAT".center(50))
    print("-" * 50)
    print(f"   👤 ID Client      : {client_id}")
    print(f"   💼 Montant total : {total_amount:.2f} €")
    print(f"   💳 Montant dû    : {amount_due:.2f} €")
    print(f"   ✍️  Signé         : {'✅ Oui' if is_signed else '❌ Non'}")
    print("-" * 50)

    confirm = input("   Confirmer la création ? (o/N) : ").strip().lower()
    if confirm != "o":
        print("   ❌ Création annulée.")
        return None

    # ——————————————————————————————————————————————————————————————
    # 📡 Appel API (envoi du payload tel quel)
    #   Remarque : le backend peut compléter/écraser sales_contact si nécessaire.
    # ——————————————————————————————————————————————————————————————
    payload = {
        "client": client_id,
        "total_amount": total_amount,
        "amount_due": amount_due,
        "is_signed": is_signed,
    }

    print("\n⏳ Enregistrement...")
    resp = session.post(CONTRACT_URL, json=payload)

    # ——————————————————————————————————————————————————————————————
    # ✅ Succès 2xx → retourne l’objet créé
    # ❌ Sinon, message d’erreur clair avec contenu de réponse
    # ——————————————————————————————————————————————————————————————
    if 200 <= resp.status_code < 300:
        contrat = resp.json()
        print(f"✅ Contrat #{contrat.get('id')} créé avec succès.")
        return contrat

    print(f"❌ Erreur HTTP {resp.status_code} lors de la création du contrat.")
    try:
        print("📨", resp.json())
    except ValueError:
        print("📨", resp.text)
    return None