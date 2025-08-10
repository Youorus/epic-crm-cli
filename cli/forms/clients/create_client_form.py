# cli/forms/clients/create_client_form.py

from datetime import date
from cli.validators.date_parser import parse_french_date
from cli.validators.email_validator import validate_email
from cli.validators.phone_validator import validate_phone
from cli.validators.exceptions import ValidationError
from cli.utils.session import session
from cli.utils.config import CLIENT_URL


def _format_fr_phone(raw: str) -> str:
    """
    Normalise un numéro FR en ajoutant l’indicatif +33 si nécessaire.

    Règles simples :
    - Commence déjà par "+"  -> inchangé (supposé déjà au format intl).
    - Commence par "0"      -> remplace par "+33" (ex: 06... -> +336...).
    - Commence par "33"     -> préfixe d'un "+" -> "+33...".
    - Sinon                  -> préfixe "+33 " (note : espace volontaire pour lisibilité CLI).
    """
    s = (raw or "").strip()
    if not s:
        return s
    if s.startswith("+"):
        return s
    if s.startswith("0"):
        return "+33" + s[1:]
    if s.startswith("33"):
        return "+" + s
    return "+33 " + s


def create_client_form():
    """
    Formulaire CLI pour créer un client (conforme au modèle Client).

    Champs requis :
      - full_name, email, phone, company_name, last_contact

    Comportement :
      - last_contact : accepte une date en français (ex: "29 mars 2025").
                       Si laissé vide, utilise la date du jour.
      - Rôle GESTION : peut préciser un sales_contact (ID d’utilisateur).
                       Pour COMMERCIAL, l’assignation se fait automatiquement côté backend
                       (sécurité : le serveur force l’auteur comme sales_contact).

    Retour :
      - dict du client créé (réponse API) en cas de succès
      - None si annulation utilisateur ou erreur
    """
    print("\n" + "=" * 50)
    print("🏢  CRÉATION D’UN CLIENT".center(50))
    print("=" * 50)
    print("(Tape 'retour' à tout moment pour annuler)\n")

    payload = {}

    # 👤 Nom complet (obligatoire)
    while True:
        full_name = input("   👤 Nom complet : ").strip()
        if full_name.lower() == "retour":
            print("   ❌ Création annulée.")
            return None
        if full_name:
            payload["full_name"] = full_name
            break
        print("   ❌ Le nom complet est requis.")

    # 📧 Email (validation stricte)
    while True:
        email = input("   📧 Email       : ").strip()
        if email.lower() == "retour":
            print("   ❌ Création annulée.")
            return None
        try:
            validate_email(email)
            payload["email"] = email
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # 📞 Téléphone (normalisation FR + validation)
    while True:
        phone_raw = input("   📞 Téléphone   : ").strip()
        if phone_raw.lower() == "retour":
            print("   ❌ Création annulée.")
            return None
        phone = _format_fr_phone(phone_raw)
        try:
            validate_phone(phone)
            payload["phone"] = phone
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # 🏢 Société (obligatoire)
    while True:
        company = input("   🏢 Société     : ").strip()
        if company.lower() == "retour":
            print("   ❌ Création annulée.")
            return None
        if company:
            payload["company_name"] = company
            break
        print("   ❌ Le nom de l’entreprise est requis.")

    # 📅 Dernier contact (vide -> aujourd'hui ; sinon parsing FR)
    while True:
        prompt_def = date.today().isoformat()
        last_contact_str = input(f"   📅 Dernier contact (ex: 29 mars 2025) [défaut {prompt_def}] : ").strip()
        if last_contact_str.lower() == "retour":
            print("   ❌ Création annulée.")
            return None
        if not last_contact_str:
            payload["last_contact"] = prompt_def
            break
        try:
            payload["last_contact"] = str(parse_french_date(last_contact_str))
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # 🎯 Sales contact (uniquement visible pour GESTION ; COMMERCIAL ignoré côté serveur)
    role = (session.user or {}).get("role")
    if role == "GESTION":
        sc = input("   🎯 ID du commercial (optionnel) : ").strip()
        if sc and sc.isdigit():
            payload["sales_contact"] = int(sc)
        elif sc and not sc.isdigit():
            print("   ⚠️ ID commercial ignoré (doit être un entier).")

    # 📋 Récapitulatif (confirmation)
    print("\n" + "-" * 50)
    print("📋  RÉCAPITULATIF".center(50))
    print("-" * 50)
    print(f"   👤 Nom complet     : {payload['full_name']}")
    print(f"   📧 Email           : {payload['email']}")
    print(f"   📞 Téléphone       : {payload['phone']}")
    print(f"   🏢 Société         : {payload['company_name']}")
    print(f"   📅 Dernier contact : {payload['last_contact']}")
    if "sales_contact" in payload:
        print(f"   🎯 Commercial ID   : {payload['sales_contact']}")
    print("-" * 50)

    confirm = input("   Confirmer la création ? (o/N) : ").strip().lower()
    if confirm != "o":
        print("   ❌ Création annulée.")
        return None

    # 🚀 Appel API
    print("\n⏳ Enregistrement du client…")
    resp = session.post(CLIENT_URL, json=payload)

    if 200 <= resp.status_code < 300:
        client = resp.json()
        print(f"✅ Client #{client.get('id')} créé : {client.get('full_name')} – {client.get('company_name')}")
        return client

    # ❗ Gestion d’erreurs lisible (ex : email déjà utilisé)
    print(f"❌ Erreur HTTP {resp.status_code} lors de la création du client.")
    try:
        err = resp.json()
        print("📨", err)
        if "email" in err and any("unique" in str(m).lower() for m in err["email"]):
            print("⚠️ Cet email est déjà utilisé par un autre client.")
    except ValueError:
        print("📨", resp.text)
    return None