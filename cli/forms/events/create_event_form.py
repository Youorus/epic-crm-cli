# cli/forms/events/create_event_form.py
from cli.utils.session import session
from cli.validators.attendees_validator import validate_attendees
from cli.validators.contract_validator import validate_contract_id
from cli.validators.exceptions import ValidationError
from cli.validators.validate_signed_contract import validate_signed_contract
from cli.validators.validate_event_dates import validate_event_dates
from cli.utils.config import EVENT_URL


def _get_contract_sales_contact_id(c: dict) -> int | None:
    """
    Retourne l'ID du commercial attaché à un contrat, quel que soit
    le format exposé par l'API.

    Gère les variantes courantes :
    - 'sales_contact' (int ou objet) ;
    - 'sales_contact_id' (int).
    """
    sc = c.get("sales_contact")
    if isinstance(sc, dict):
        return sc.get("id")
    if isinstance(sc, int):
        return sc
    return c.get("sales_contact_id")


def _iso_minutes(dt) -> str:
    """
    Formate un datetime en ISO 8601 à la minute (sans microsecondes),
    compatible avec DRF et la plupart des backends.
    """
    return dt.replace(second=0, microsecond=0).isoformat()


def create_event_form(signed_contracts: list[dict]):
    """
    Formulaire CLI de création d’un événement.

    Flux :
      1) Affiche les contrats signés disponibles.
      2) Sélection du contrat (avec contrôle : un COMMERCIAL ne peut agir
         que sur ses propres contrats).
      3) Saisie des champs requis : nom, lieu, participants, début, fin.
      4) Déduit automatiquement le client depuis le contrat.
      5) Affiche un récapitulatif et demande confirmation.
      6) POST direct vers l’API ; retourne l’événement créé ou None.

    Contraintes métier :
      - Un événement est lié OneToOne à un contrat (un seul événement par contrat).
      - Le support_contact n’est pas demandé ici (sera assigné plus tard par GESTION).
      - Le client est imposé par le contrat (évite les incohérences).

    Args:
        signed_contracts (list[dict]): liste de contrats signés visibles par l’utilisateur.

    Returns:
        dict | None: L’événement créé si succès, sinon None.
    """
    # ——————————————————————————————————————————————————————————————
    # 🧾 En-tête et vérifications préalables
    # ——————————————————————————————————————————————————————————————
    print("\n" + "=" * 50)
    print("🗓️  CRÉATION D’UN ÉVÉNEMENT".center(50))
    print("=" * 50)
    print("(Tape 'retour' à tout moment pour annuler)\n")

    if not signed_contracts:
        print("⚠️ Aucun contrat signé disponible.")
        return None

    # ——————————————————————————————————————————————————————————————
    # 📋 Affichage des contrats signés disponibles (contexte utilisateur)
    # ——————————————————————————————————————————————————————————————
    print("📄 Contrats signés disponibles :")
    for c in signed_contracts:
        total = float(c.get("total_amount") or 0)
        due = float(c.get("amount_due") or 0)
        paid = max(total - due, 0.0)
        client_label = c.get("client_full_name") or f"Client #{c.get('client')}"
        sales_label = c.get("sales_contact_username") or _get_contract_sales_contact_id(c) or "—"
        print(
            f"  ➤ ID: {c['id']} | {client_label} | "
            f"Montant: {total:.2f} € | Payé: {paid:.2f} € | "
            f"Commercial: {sales_label} | Signé: {'✅' if c.get('is_signed') else '❌'}"
        )

    # ——————————————————————————————————————————————————————————————
    # 🔗 Sélection du contrat + contrôle rôle (COMMERCIAL)
    # ——————————————————————————————————————————————————————————————
    current_user = session.user or {}
    current_user_id = current_user.get("id")
    current_role = current_user.get("role")

    while True:
        contract_id_input = input("\n🔗 ID du contrat : ").strip()
        if contract_id_input.lower() == "retour":
            return None
        try:
            # Validation : l’ID doit appartenir à la liste fournie
            contract_id = validate_contract_id(contract_id_input, signed_contracts)
            # Validation : le contrat doit être signé (défense supplémentaire)
            validate_signed_contract(contract_id, signed_contracts)

            # Récupération du contrat sélectionné
            contract = next((c for c in signed_contracts if c["id"] == contract_id), None)
            if not contract:
                print("❌ Contrat introuvable.")
                continue

            # Règle métier : un COMMERCIAL ne peut créer un événement que pour ses contrats
            if current_role == "COMMERCIAL":
                sc_id = _get_contract_sales_contact_id(contract)
                if sc_id is not None and str(sc_id) != str(current_user_id):
                    print("❌ Vous ne pouvez créer un événement que pour vos propres contrats.")
                    continue

            break
        except ValidationError as e:
            print(f"❌ {e}")

    # ——————————————————————————————————————————————————————————————
    # 🧾 Saisie des champs de l’événement (validations dédiées)
    # ——————————————————————————————————————————————————————————————
    # 📛 Nom
    while True:
        event_name = input("📛 Nom de l'événement : ").strip()
        if event_name.lower() == "retour":
            return None
        if not event_name:
            print("❌ Le nom ne peut pas être vide.")
            continue
        break

    # 📍 Lieu
    while True:
        location = input("📍 Lieu : ").strip()
        if location.lower() == "retour":
            return None
        if not location:
            print("❌ Le lieu est requis.")
            continue
        break

    # 👥 Participants
    while True:
        attendees_input = input("👥 Nombre de participants : ").strip()
        if attendees_input.lower() == "retour":
            return None
        try:
            attendees = validate_attendees(attendees_input)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # 🕒 Début / 🕓 Fin (parse via validateur commun)
    while True:
        start_input = input("🕒 Date/heure de début (ex: 29 mai 2025 à 14h) : ").strip()
        if start_input.lower() == "retour":
            return None

        end_input = input("🕓 Date/heure de fin (ex: 30 mai 2025 à 16h) : ").strip()
        if end_input.lower() == "retour":
            return None

        try:
            start_dt, end_dt = validate_event_dates(start_input, end_input)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # ——————————————————————————————————————————————————————————————
    # 🔗 Le client est déduit automatiquement depuis le contrat
    # ——————————————————————————————————————————————————————————————
    client_id = contract.get("client")
    if not client_id:
        print("❌ Impossible de déterminer le client depuis le contrat sélectionné.")
        return None

    # ——————————————————————————————————————————————————————————————
    # 📋 Récapitulatif avant envoi
    # ——————————————————————————————————————————————————————————————
    print("\n" + "-" * 50)
    print("📋  RÉCAPITULATIF DE L’ÉVÉNEMENT".center(50))
    print("-" * 50)
    print(f"   🔗 Contrat       : {contract_id}")
    print(f"   👤 Client        : {client_id}")
    print(f"   📛 Nom           : {event_name}")
    print(f"   📍 Lieu          : {location}")
    print(f"   👥 Participants  : {attendees}")
    print(f"   🕒 Début         : {_iso_minutes(start_dt)}")
    print(f"   🕓 Fin           : {_iso_minutes(end_dt)}")
    print("-" * 50)

    confirm = input("   Confirmer la création ? (o/N) : ").strip().lower()
    if confirm != "o":
        print("   ❌ Création annulée.")
        return None

    # ——————————————————————————————————————————————————————————————
    # 🚀 POST API (aligné au modèle Event)
    # ——————————————————————————————————————————————————————————————
    payload = {
        "contract": contract_id,
        "client": client_id,  # imposé par la règle métier (dérivé du contrat)
        "event_name": event_name,
        "event_start": _iso_minutes(start_dt),
        "event_end": _iso_minutes(end_dt),
        "location": location,
        "attendees": attendees,
        "notes": input("📝 Notes (facultatif) : ").strip(),
        # support_contact non envoyé ici (assigné par GESTION plus tard)
    }

    print("\n⏳ Enregistrement de l’événement…")
    resp = session.post(EVENT_URL, json=payload)

    if 200 <= resp.status_code < 300:
        event = resp.json()
        print(f"✅ Événement #{event.get('id')} créé avec succès pour le contrat #{contract_id}.")
        return event

    # ——————————————————————————————————————————————————————————————
    # 🧯 Gestion d’erreurs (messages utiles côté CLI)
    # ——————————————————————————————————————————————————————————————
    print(f"❌ Erreur HTTP {resp.status_code} lors de la création de l’événement.")
    try:
        err = resp.json()
        print("📨", err)
        # Cas classique : OneToOne déjà utilisé (événement déjà existant pour ce contrat)
        if "contract" in err and any("unique" in str(m).lower() for m in err["contract"]):
            print("⚠️ Un événement existe déjà pour ce contrat (relation OneToOne).")
    except ValueError:
        print("📨", resp.text)
    return None