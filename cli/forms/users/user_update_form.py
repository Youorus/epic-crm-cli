# cli/forms/user_update_form.py

from typing import Optional, Dict, Any

from cli.validators.exceptions import ValidationError
from cli.validators.email_validator import validate_email
from cli.utils.session import session
from cli.utils.config import USER_URL


def update_user_form() -> Optional[Dict[str, Any]]:
    """
    Formulaire CLI pour modifier un collaborateur existant.

    Comportement :
      - Permet de laisser un champ vide pour ne pas le modifier.
      - Valide les champs sensibles (email, mot de passe, rôle).
      - Demande une confirmation avant envoi.
      - Envoie directement la requête PATCH à l'API via la session globale.

    Retour :
      - dict : payload envoyé en cas de succès (pour éventuel logging/trace).
      - None : si l'action est annulée ou en cas d'erreur.
    """
    print("\n" + "=" * 50)
    print("🛠️ MODIFICATION D’UN COLLABORATEUR".center(50))
    print("=" * 50)
    print("(Tape 'retour' à tout moment pour annuler)\n")

    # ─────────────────────────────────────────────────────────────
    # 🔢 Saisie de l'ID
    # ─────────────────────────────────────────────────────────────
    while True:
        user_id_str = input("🔢 ID de l'utilisateur à modifier : ").strip()
        if user_id_str.lower() == "retour":
            return None
        if user_id_str.isdigit():
            user_id = int(user_id_str)
            break
        print("❌ L'ID doit être un nombre entier.")

    payload: Dict[str, Any] = {}

    # ─────────────────────────────────────────────────────────────
    # 🆔 Nom d'utilisateur (optionnel)
    # ─────────────────────────────────────────────────────────────
    username = input("🆔 Nom d'utilisateur (laisser vide pour ne pas changer) : ").strip()
    if username.lower() == "retour":
        return None
    if username:
        payload["username"] = username

    # ─────────────────────────────────────────────────────────────
    # 📧 Email (optionnel + validation)
    # ─────────────────────────────────────────────────────────────
    email = input("📧 Email (laisser vide pour ne pas changer) : ").strip()
    if email.lower() == "retour":
        return None
    if email:
        try:
            validate_email(email)
            payload["email"] = email
        except ValidationError as exc:
            # On n'annule pas tout : on ignore ce champ invalide
            print(f"❌ Email ignoré : {exc}")

    # ─────────────────────────────────────────────────────────────
    # 🔑 Mot de passe (optionnel + minimum 8)
    # ─────────────────────────────────────────────────────────────
    password = input("🔑 Mot de passe (laisser vide pour ne pas changer) : ").strip()
    if password.lower() == "retour":
        return None
    if password:
        if len(password) < 8:
            print("❌ Mot de passe ignoré (trop court).")
        else:
            payload["password"] = password

    # ─────────────────────────────────────────────────────────────
    # 🎯 Rôle (optionnel + contrôle)
    # ─────────────────────────────────────────────────────────────
    ROLES = ("COMMERCIAL", "SUPPORT", "GESTION")
    print("\nRôles disponibles : " + " / ".join(ROLES))
    role = input("🎯 Rôle (laisser vide pour ne pas changer) : ").strip().upper()
    if role.lower() == "retour":
        return None
    if role:
        if role in ROLES:
            # Petite barrière UX : si un non-GESTION tente de changer un rôle,
            # on n’empêche pas ici (c’est le backend qui tranche), mais on informe.
            current_user = session.user or {}
            if current_user.get("role") != "GESTION":
                print("ℹ️ Seul le rôle GESTION est autorisé à modifier les rôles (vérifié côté API).")
            payload["role"] = role
        else:
            print(f"❌ Rôle ignoré (invalide). Choix valides : {', '.join(ROLES)}")

    # Rien à mettre à jour ?
    if not payload:
        print("⚠️ Aucun changement à effectuer.")
        return None

    # ─────────────────────────────────────────────────────────────
    # 📋 Récapitulatif et confirmation
    # ─────────────────────────────────────────────────────────────
    print("\n" + "-" * 50)
    print("📋  MODIFICATIONS PROPOSÉES".center(50))
    print("-" * 50)
    for key, value in payload.items():
        # On évite d'afficher le mot de passe en clair
        safe_value = "********" if key == "password" else value
        print(f"   {key} : {safe_value}")
    print("-" * 50)

    confirm = input("   Confirmer la mise à jour ? (o/N) : ").strip().lower()
    if confirm != "o":
        print("❌ Modification annulée.")
        return None

    # ─────────────────────────────────────────────────────────────
    # 📨 Appel API (PATCH)
    # ─────────────────────────────────────────────────────────────
    try:
        resp = session.patch(f"{USER_URL}{user_id}/", json=payload)
    except Exception as exc:
        print(f"❌ Impossible de contacter le serveur : {exc}")
        return None

    if resp.status_code == 200:
        print(f"✅ Collaborateur #{user_id} modifié avec succès.")
        return payload

    # Gestion d’erreurs lisible
    if resp.status_code == 403:
        print("⛔ Permission refusée : vous n’êtes pas autorisé à modifier cet utilisateur.")
    elif resp.status_code == 404:
        print("❌ Utilisateur introuvable.")
    elif resp.status_code == 400:
        print("❌ Données invalides :")
        try:
            print(resp.json())
        except ValueError:
            print(resp.text)
    else:
        print(f"❌ Erreur lors de la modification (HTTP {resp.status_code}) :")
        try:
            print(resp.json())
        except ValueError:
            print(resp.text)

    return None