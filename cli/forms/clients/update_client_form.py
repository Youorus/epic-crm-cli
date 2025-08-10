# cli/forms/update_client_form.py
from datetime import datetime, date
from cli.validators.exceptions import ValidationError
from cli.validators.email_validator import validate_email
from cli.validators.phone_validator import validate_phone
from cli.utils.session import session
from cli.utils.config import CLIENT_URL


def _parse_date_yyyy_mm_dd(s: str) -> str:
    """
    Valide une date au format ISO court « YYYY-MM-DD » et
    retourne la chaîne normalisée via .isoformat().

    Args:
        s: Chaîne saisie par l'utilisateur (ex: "2025-08-09").

    Returns:
        str: La date au format "YYYY-MM-DD".

    Raises:
        ValidationError: Si la chaîne ne respecte pas le format attendu.
    """
    try:
        return datetime.strptime(s, "%Y-%m-%d").date().isoformat()
    except Exception:
        raise ValidationError("La date doit être au format YYYY-MM-DD (ex: 2025-08-09).")


def _format_fr_phone(raw: str) -> str:
    """
    Normalise un numéro FR en ajoutant l’indicatif +33 si nécessaire.

    Règles :
      - Commence par "+"  : inchangé (déjà au format international).
      - Commence par "0"  : converti en +33 + numéro sans le 0 (ex: 06... -> +336...).
      - Commence par "33" : on préfixe simplement d’un "+" -> +33...
      - Sinon             : on préfixe par "+33 " (espace conservé pour lisibilité en CLI).

    Args:
        raw: Chaîne telle que saisie par l'utilisateur.

    Returns:
        str: Numéro normalisé.
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


def update_client_form(client_id: int):
    """
    Formulaire CLI pour mettre à jour un client.

    Comportement :
      - Récupère l’état courant du client pour afficher des valeurs par défaut.
      - Entrée vide => conserve la valeur actuelle.
      - Valide l'email, le téléphone (après normalisation) et la date.
      - Pour le rôle GESTION, autorise la modification du sales_contact.
      - Effectue un PATCH vers l’API et affiche un récapitulatif avant confirmation.

    Args:
        client_id: Identifiant du client à modifier.

    Returns:
        dict | None: L'objet client mis à jour (réponse API) si succès, sinon None.
    """
    # 🔎 Récupération de l'objet existant (et signalement des erreurs d’accès)
    print(f"\n⏳ Chargement du client #{client_id}...")
    resp = session.get(f"{CLIENT_URL}{client_id}/")
    if resp.status_code != 200:
        # 404 attendu si le commercial n'est pas propriétaire (selon get_queryset)
        # ou 403 selon la permission ; on rend le message plus explicite.
        if resp.status_code == 404:
            print("❌ Client introuvable (ou vous n’y avez pas accès).")
        else:
            try:
                print(f"❌ Erreur ({resp.status_code}) :", resp.json())
            except ValueError:
                print(f"❌ Erreur ({resp.status_code}) :", resp.text)
        return None

    client = resp.json()
    role = (session.user or {}).get("role")

    # 🖊️ Formulaire interactif
    print("\n" + "=" * 50)
    print(f"✏️  MODIFICATION CLIENT #{client_id}".center(50))
    print("=" * 50 + "\n")

    # 👤 Nom complet (laisser vide pour conserver)
    full_name_raw = input(f"   👤 Nom complet [{client.get('full_name','')}] : ").strip()
    full_name = full_name_raw or client.get("full_name")

    # 📧 Email (validation stricte ; entrée vide => conserve)
    while True:
        email_raw = input(f"   📧 Email [{client.get('email','')}] : ").strip()
        if not email_raw:
            email = client.get("email")
            break
        try:
            validate_email(email_raw)
            email = email_raw
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # 📞 Téléphone (normalisation + validation ; entrée vide => conserve)
    while True:
        phone_raw = input(f"   📞 Téléphone [{client.get('phone','')}] : ").strip()
        if not phone_raw:
            phone = client.get("phone")
            break
        phone = _format_fr_phone(phone_raw)
        try:
            validate_phone(phone)
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # 🏢 Société (entrée vide => conserve)
    company_raw = input(f"   🏢 Société [{client.get('company_name','')}] : ").strip()
    company_name = company_raw or client.get("company_name")

    # 📅 Dernier contact (format ISO requis ; entrée vide => conserve)
    while True:
        default_last = client.get('last_contact', date.today().isoformat())
        last_contact_raw = input(f"   📅 Dernier contact (YYYY-MM-DD) [{default_last}] : ").strip()
        if not last_contact_raw:
            last_contact = client.get("last_contact")
            break
        try:
            last_contact = _parse_date_yyyy_mm_dd(last_contact_raw)
            break
        except ValidationError as e:
            print(f"   ❌ {e}")

    # 🎯 Commercial (modifiable uniquement pour GESTION)
    sales_contact = client.get("sales_contact")
    if role == "GESTION":
        sc_raw = input(f"   🎯 ID Commercial assigné [{sales_contact if sales_contact else ''}] : ").strip()
        if sc_raw:
            if sc_raw.isdigit():
                sales_contact = int(sc_raw)
            else:
                print("   ❌ L’ID commercial doit être un entier. Valeur ignorée.")

    # 🔁 Détection d’absence de modifications pour éviter un PATCH inutile
    no_change = (
        full_name == client.get("full_name")
        and email == client.get("email")
        and phone == client.get("phone")
        and company_name == client.get("company_name")
        and last_contact == client.get("last_contact")
        and (role != "GESTION" or sales_contact == client.get("sales_contact"))
    )
    if no_change:
        print("ℹ️  Aucun changement détecté. Rien à mettre à jour.")
        return client

    # 📋 Récapitulatif avant envoi
    print("\n" + "-" * 50)
    print("📋   RÉCAPITULATIF DE LA MODIFICATION".center(50))
    print("-" * 50)
    print(f"   👤 Nom complet     : {full_name}")
    print(f"   📧 Email           : {email}")
    print(f"   📞 Téléphone       : {phone}")
    print(f"   🏢 Société         : {company_name}")
    print(f"   📅 Dernier contact : {last_contact}")
    if role == "GESTION":
        print(f"   🎯 Commercial ID   : {sales_contact}")
    print("-" * 50)

    confirm = input("   Confirmer la modification ? (o/N) : ").strip().lower()
    if confirm != "o":
        print("   ❌ Modification annulée.")
        return None

    # 📡 Envoi PATCH (on n’envoie que les champs utiles)
    payload = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "company_name": company_name,
        "last_contact": last_contact,
    }
    if role == "GESTION":
        payload["sales_contact"] = sales_contact

    print("\n⏳ Mise à jour du client...")
    resp = session.patch(f"{CLIENT_URL}{client_id}/", json=payload)

    # ✅ Succès
    if 200 <= resp.status_code < 300:
        updated = resp.json()
        print(f"✅ Client #{updated.get('id')} mis à jour avec succès.")
        return updated

    # ❗ Gestion d’erreurs lisible
    if resp.status_code == 403:
        print("⛔ Permission refusée : vous ne pouvez modifier que vos propres clients.")
    elif resp.status_code == 404:
        print("❌ Client introuvable (ou vous n’y avez pas accès).")
    else:
        try:
            print(f"❌ Erreur HTTP {resp.status_code} :", resp.json())
        except ValueError:
            print(f"❌ Erreur HTTP {resp.status_code} :", resp.text)
    return None