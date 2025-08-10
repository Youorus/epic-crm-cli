# cli/forms/create_user_form.py

from typing import Optional

from cli.validators.exceptions import ValidationError
from cli.validators.email_validator import validate_email
from cli.utils.session import session
from cli.utils.config import USER_URL


# Constantes de validation
_MIN_PASSWORD_LEN = 8
_ROLES = ("COMMERCIAL", "SUPPORT", "GESTION")


def _validate_password(pwd: str) -> bool:
    """Vérifie la longueur minimale du mot de passe (sans règles complexes)."""
    return len(pwd) >= _MIN_PASSWORD_LEN


def create_user_form() -> Optional[dict]:
    """
    Formulaire CLI pour créer un collaborateur et l'envoyer directement à l'API.

    Comportement :
      - Demande les champs requis (username, email, mot de passe, rôle)
      - Valide l’email et la longueur du mot de passe
      - Force le rôle à appartenir à la liste contrôlée
      - Affiche un récapitulatif et demande confirmation
      - Envoie la requête POST via la session globale

    Retour :
      - dict des données envoyées si tout s’est bien passé
      - None en cas d’annulation utilisateur ou d’erreur bloquante
    """
    print("\n" + "=" * 50)
    print("👤 CRÉATION D’UN COLLABORATEUR".center(50))
    print("=" * 50)
    print("(Tape 'retour' à tout moment pour annuler)\n")

    data: dict = {}

    # ─────────────────────────────────────────────────────────────
    # 🆔 Nom d'utilisateur
    # ─────────────────────────────────────────────────────────────
    while True:
        username = input("🆔 Nom d'utilisateur : ").strip()
        if username.lower() == "retour":
            return None
        if username:
            data["username"] = username
            break
        print("❌ Le nom d'utilisateur ne peut pas être vide.")

    # ─────────────────────────────────────────────────────────────
    # 📧 Email (validation fonctionnelle)
    # ─────────────────────────────────────────────────────────────
    while True:
        email = input("📧 Email : ").strip()
        if email.lower() == "retour":
            return None
        try:
            validate_email(email)
            data["email"] = email
            break
        except ValidationError as e:
            print(f"❌ {e}")

    # ─────────────────────────────────────────────────────────────
    # 🔑 Mot de passe (contrôle longueur minimale)
    # ─────────────────────────────────────────────────────────────
    while True:
        password = input(f"🔑 Mot de passe (min {_MIN_PASSWORD_LEN} caractères) : ").strip()
        if password.lower() == "retour":
            return None
        if not _validate_password(password):
            print(f"❌ Le mot de passe doit contenir au moins {_MIN_PASSWORD_LEN} caractères.")
            continue
        data["password"] = password
        break

    # ─────────────────────────────────────────────────────────────
    # 🎯 Rôle (liste contrôlée)
    # ─────────────────────────────────────────────────────────────
    print("\nRôles disponibles : " + " / ".join(_ROLES))
    while True:
        role = input("🎯 Rôle : ").strip().upper()
        if role.lower() == "retour":
            return None
        if role in _ROLES:
            data["role"] = role
            break
        print(f"❌ Rôle invalide. Choix valides : {', '.join(_ROLES)}")

    # ─────────────────────────────────────────────────────────────
    # 📋 Récapitulatif + confirmation
    # ─────────────────────────────────────────────────────────────
    print("\n" + "-" * 50)
    print("📋  RÉCAPITULATIF".center(50))
    print("-" * 50)
    print(f"   🆔 Nom d'utilisateur : {data['username']}")
    print(f"   📧 Email            : {data['email']}")
    print(f"   🎯 Rôle             : {data['role']}")
    print("-" * 50)
    confirm = input("   Confirmer la création ? (o/N) : ").strip().lower()
    if confirm != "o":
        print("❌ Création annulée.")
        return None

    # ─────────────────────────────────────────────────────────────
    # 🚀 Appel API (POST via session)
    # ─────────────────────────────────────────────────────────────
    try:
        resp = session.post(USER_URL, json=data)
    except Exception as exc:
        print(f"❌ Impossible de contacter le serveur : {exc}")
        return None

    if resp.status_code in (200, 201):
        print(f"✅ Collaborateur '{data['username']}' créé avec succès.")
        # On retourne les données utiles (la réponse peut aussi être lue si besoin)
        return data

    # Gestion lisible des erreurs HTTP (JSON ou texte brut)
    print("❌ Erreur lors de la création du collaborateur :")
    try:
        print(resp.json())
    except ValueError:
        print(resp.text)
    return None