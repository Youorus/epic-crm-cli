# cli/forms/create_client_form.py

from __future__ import annotations

from datetime import datetime, date
from typing import Optional, Dict, Any

from cli.validators.exceptions import ValidationError
from cli.validators.email_validator import validate_email
from cli.utils.session import session
from cli.utils.config import CLIENT_URL


def _parse_date_yyyy_mm_dd(s: str) -> str:
    """
    Valide une date au format ISO 'YYYY-MM-DD' et renvoie la même chaîne
    si elle est correcte. Soulève ValidationError en cas d’échec.

    Exemple valide : '2025-08-09'
    """
    try:
        dt = datetime.strptime(s, "%Y-%m-%d").date()
        return dt.isoformat()
    except Exception:
        raise ValidationError("La date doit être au format YYYY-MM-DD (ex: 2025-08-09).")


def create_client_form() -> Optional[Dict[str, Any]]:
    """
    Formulaire CLI pour créer un client (conforme au modèle).
    Champs requis :
      - full_name, email, phone, company_name, last_contact
    Champs optionnels (automatique côté backend pour un COMMERCIAL) :
      - sales_contact (uniquement saisi ici si role = GESTION)

    Retour :
      - dict (payload) du client créé en cas de succès
      - None si annulé ou en cas d’erreur serveur
    """
    print("\n" + "=" * 50)
    print("🏢   FORMULAIRE DE CRÉATION DE CLIENT".center(50))
    print("=" * 50 + "\n")
    print("(Tape 'retour' à tout moment pour annuler)\n")

    data: Dict[str, Any] = {}

    # Petite aide interne : gère l’annulation de saisie
    def _cancel_if_requested(value: str) -> bool:
        if value.lower() == "retour":
            print("   ❌ Création annulée.")
            return True
        return False

    # 👤 Nom complet
    while True:
        full_name = input("   👤 Nom complet           : ").strip()
        if _cancel_if_requested(full_name):
            return None
        if full_name:
            data["full_name"] = full_name
            break
        print("   ❌ Le nom complet est requis.")

    # 📧 Email
    while True:
        email = input("   📧 Email                 : ").strip()
        if _cancel_if_requested(email):
            return None
        try:
            validate_email(email)
            data["email"] = email
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # 📞 Téléphone (aucune validation modifiée pour ne rien casser)
    while True:
        phone = input("   📞 Téléphone             : ").strip()
        if _cancel_if_requested(phone):
            return None
        if phone:
            data["phone"] = phone
            break
        print("   ❌ Le téléphone est requis.")

    # 🏢 Société
    while True:
        company_name = input("   🏢 Société               : ").strip()
        if _cancel_if_requested(company_name):
            return None
        if company_name:
            data["company_name"] = company_name
            break
        print("   ❌ Le nom de la société est requis.")

    # 📅 Dernier contact (requis par le modèle)
    while True:
        default_today = date.today().isoformat()
        last_contact = input(
            f"   📅 Dernier contact (YYYY-MM-DD) [defaut {default_today}] : "
        ).strip()
        if _cancel_if_requested(last_contact):
            return None

        if not last_contact:
            data["last_contact"] = default_today
            break

        try:
            data["last_contact"] = _parse_date_yyyy_mm_dd(last_contact)
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # 🎯 Sales contact (uniquement visible/saisi si l’utilisateur connecté est GESTION)
    role = (session.user or {}).get("role")
    if role == "GESTION":
        choice = input("   🎯 Assigner un commercial (ID utilisateur) [laisser vide pour aucun] : ").strip()
        if choice and choice.isdigit():
            data["sales_contact"] = int(choice)

    # 📋 Récapitulatif (affichage)
    print("\n" + "-" * 50)
    print("📋   RÉCAPITULATIF DU CLIENT".center(50))
    print("-" * 50)
    print(f"   👤 Nom complet     : {data['full_name']}")
    print(f"   📧 Email           : {data['email']}")
    print(f"   📞 Téléphone       : {data['phone']}")
    print(f"   🏢 Société         : {data['company_name']}")
    print(f"   📅 Dernier contact : {data['last_contact']}")
    if "sales_contact" in data:
        print(f"   🎯 Commercial ID   : {data['sales_contact']}")
    print("-" * 50)

    # Confirmation
    confirm = input("   Confirmer la création ? (o/N) : ").strip().lower()
    if confirm != "o":
        print("   ❌ Création annulée.")
        return None

    # 📡 Appel API (ne rien changer au flux actuel)
    print("\n⏳ Enregistrement...")
    resp = session.post(CLIENT_URL, json=data)

    if 200 <= resp.status_code < 300:
        client = resp.json()
        print(f"✅ Client #{client.get('id')} créé avec succès.")
        return client

    # Gestion d’erreur (lisible mais inchangée côté logique)
    print(f"❌ Erreur HTTP {resp.status_code} lors de la création du client.")
    try:
        print("📨", resp.json())
    except ValueError:
        print("📨", resp.text)
    return None