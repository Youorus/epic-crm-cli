# cli/forms/update_contract_form.py

from cli.validators.exceptions import ValidationError
from cli.validators.validate_amount import validate_amount
from cli.validators.validate_signed_input import validate_signed_input
from cli.utils.session import session
from cli.utils.config import CONTRACT_URL


def update_contract_form(contract_id: int):
    """
    Formulaire CLI pour mettre à jour un contrat existant.

    Fonctionnement :
      1. Récupère les données actuelles du contrat via l'API.
      2. Affiche les valeurs actuelles.
      3. Permet à l'utilisateur de modifier chaque champ :
         - Montant total (total_amount)
         - Montant dû (amount_due)
         - Statut signé (is_signed)
      4. Entrée vide → conserve la valeur existante.
      5. Entrée "retour" → annule la modification.
      6. Validation forte via validators dédiés.
      7. Si modification → PATCH vers l'API.
      8. Retourne le contrat mis à jour ou None si annulé/erreur.

    Args:
        contract_id (int): ID du contrat à modifier.

    Returns:
        dict | None: Contrat mis à jour si succès, None sinon.
    """
    # ——————————————————————————————————————————————————————————————
    # 📡 Étape 1 : Récupération du contrat depuis l’API
    # ——————————————————————————————————————————————————————————————
    print(f"\n⏳ Chargement du contrat #{contract_id}...")
    resp = session.get(f"{CONTRACT_URL}{contract_id}/")
    if resp.status_code != 200:
        print(f"❌ Impossible de récupérer le contrat ({resp.status_code}).")
        try:
            print("📨", resp.json())
        except ValueError:
            print("📨", resp.text)
        return None

    # Conversion des données existantes pour usage interne
    contract = resp.json()
    current_total = float(contract.get("total_amount") or 0)
    current_due = float(contract.get("amount_due") or 0)
    current_signed = bool(contract.get("is_signed", False))

    print("\n" + "=" * 50)
    print(f"✏️  MODIFICATION CONTRAT #{contract_id}".center(50))
    print("=" * 50 + "\n")

    # ——————————————————————————————————————————————————————————————
    # 👤 Client (non modifiable dans ce formulaire)
    # ——————————————————————————————————————————————————————————————
    print(f"   👤 Client ID (fixe) : {contract.get('client')}")

    # ——————————————————————————————————————————————————————————————
    # 💼 Montant total
    # ——————————————————————————————————————————————————————————————
    while True:
        total_amount_raw = input(
            f"   💼 Montant total (€) [{current_total:.2f}] : "
        ).strip()

        if total_amount_raw.lower() == "retour":
            print("   ❌ Modification annulée.")
            return None

        if not total_amount_raw:
            total_amount = current_total
            break

        try:
            total_amount = validate_amount(total_amount_raw)
            if total_amount < 0:
                print("   ❌ Le montant total ne peut pas être négatif.")
                continue
            total_amount = round(float(total_amount), 2)
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # ——————————————————————————————————————————————————————————————
    # 💳 Montant dû (validation stricte + cohérence avec total_amount)
    # ——————————————————————————————————————————————————————————————
    while True:
        amount_due_raw = input(
            f"   💳 Montant dû (€) [{current_due:.2f}] : "
        ).strip()

        if amount_due_raw.lower() == "retour":
            print("   ❌ Modification annulée.")
            return None

        if not amount_due_raw:
            amount_due = current_due
        else:
            try:
                amount_due = validate_amount(amount_due_raw)
            except ValidationError as e:
                print(f"   ❌ {e}")
                continue

        try:
            amount_due = round(float(amount_due), 2)
        except (TypeError, ValueError):
            print("   ❌ Montant dû invalide.")
            continue

        if amount_due < 0:
            print("   ❌ Le montant dû ne peut pas être négatif.")
            continue

        if amount_due > total_amount:
            print("   ❌ Le montant dû ne peut pas dépasser le montant total.")
            continue

        break

    # ——————————————————————————————————————————————————————————————
    # ✅ Statut signé
    # ——————————————————————————————————————————————————————————————
    while True:
        default_signed_str = "oui" if current_signed else "non"
        signed_raw = input(
            f"   ✍️  Contrat signé ? (oui/non) [{default_signed_str}] : "
        ).strip().lower()

        if signed_raw == "retour":
            print("   ❌ Modification annulée.")
            return None

        if not signed_raw:
            is_signed = current_signed
            break
        try:
            is_signed = validate_signed_input(signed_raw)
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # ——————————————————————————————————————————————————————————————
    # 🔁 Vérification des changements
    # ——————————————————————————————————————————————————————————————
    no_change = (
        round(total_amount, 2) == round(current_total, 2)
        and round(amount_due, 2) == round(current_due, 2)
        and bool(is_signed) == bool(current_signed)
    )
    if no_change:
        print("ℹ️  Aucun changement détecté. Rien à mettre à jour.")
        return contract

    # ——————————————————————————————————————————————————————————————
    # 📋 Récapitulatif des modifications
    # ——————————————————————————————————————————————————————————————
    print("\n" + "-" * 50)
    print("📋   RÉCAPITULATIF DE LA MODIFICATION".center(50))
    print("-" * 50)
    print(f"   👤 ID Client      : {contract.get('client')}")
    print(f"   💼 Montant total : {total_amount:.2f} €")
    print(f"   💳 Montant dû    : {amount_due:.2f} €")
    print(f"   ✍️  Signé         : {'✅ Oui' if is_signed else '❌ Non'}")
    print("-" * 50)

    confirm = input("   Confirmer la modification ? (o/N) : ").strip().lower()
    if confirm != "o":
        print("   ❌ Modification annulée.")
        return None

    # ——————————————————————————————————————————————————————————————
    # 📡 Envoi PATCH à l’API
    # ——————————————————————————————————————————————————————————————
    payload = {
        "total_amount": round(total_amount, 2),
        "amount_due": round(amount_due, 2),
        "is_signed": bool(is_signed),
    }

    print("\n⏳ Mise à jour du contrat...")
    resp = session.patch(f"{CONTRACT_URL}{contract_id}/", json=payload)

    if 200 <= resp.status_code < 300:
        updated_contract = resp.json()
        print(f"✅ Contrat #{updated_contract.get('id')} mis à jour avec succès.")
        return updated_contract

    print(f"❌ Erreur HTTP {resp.status_code} lors de la mise à jour du contrat.")
    try:
        print("📨", resp.json())
    except ValueError:
        print("📨", resp.text)
    return None