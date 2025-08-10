# cli/forms/delete_user_form.py

from typing import Optional

from cli.utils.session import session
from cli.utils.config import USER_URL


def delete_user_form() -> Optional[int]:
    """
    Formulaire CLI pour supprimer un collaborateur.

    Comportement :
      - Demande un ID numérique (annulation possible avec 'retour')
      - Demande une confirmation explicite
      - Envoie la requête DELETE à l'API via la session globale
      - Affiche un message de succès/erreur lisible

    Retour :
      - int : l'ID supprimé en cas de succès
      - None : si annulé par l'utilisateur ou en cas d'erreur
    """
    print("\n" + "=" * 50)
    print("🗑️ SUPPRESSION D’UN COLLABORATEUR".center(50))
    print("=" * 50)
    print("(Tape 'retour' à tout moment pour annuler)\n")

    # ─────────────────────────────────────────────────────────────
    # 🔢 Saisie de l'ID utilisateur à supprimer
    # ─────────────────────────────────────────────────────────────
    while True:
        user_id_str = input("🔢 ID de l'utilisateur à supprimer : ").strip()
        if user_id_str.lower() == "retour":
            print("❌ Suppression annulée.")
            return None
        if user_id_str.isdigit():
            user_id = int(user_id_str)
            break
        print("❌ L'ID doit être un nombre entier.")

    # Optionnel : empêcher la suppression de soi-même (sécurité UX)
    current_user = session.user or {}
    if current_user.get("id") == user_id:
        print("⛔ Vous ne pouvez pas supprimer votre propre compte depuis ce formulaire.")
        return None

    # ─────────────────────────────────────────────────────────────
    # ⚠️ Confirmation explicite
    # ─────────────────────────────────────────────────────────────
    print("\n⚠️ ATTENTION : Cette action est IRRÉVERSIBLE !")
    confirm = input(f"   Confirmer la suppression de l’utilisateur #{user_id} ? (o/N) : ").strip().lower()
    if confirm != "o":
        print("❌ Suppression annulée.")
        return None

    # ─────────────────────────────────────────────────────────────
    # 📨 Appel API (DELETE)
    # ─────────────────────────────────────────────────────────────
    try:
        resp = session.delete(f"{USER_URL}{user_id}/")
    except Exception as exc:
        print(f"❌ Impossible de contacter le serveur : {exc}")
        return None

    # 204 No Content attendu en cas de succès
    if resp.status_code == 204:
        print(f"✅ Collaborateur #{user_id} supprimé avec succès.")
        return user_id

    # Gestion d’erreurs lisible (401/403/404/4xx/5xx)
    if resp.status_code == 404:
        print("❌ Utilisateur introuvable.")
    elif resp.status_code == 403:
        print("⛔ Permission refusée : vous n’êtes pas autorisé à supprimer cet utilisateur.")
    else:
        print(f"❌ Erreur HTTP {resp.status_code} lors de la suppression :")
        try:
            print(resp.json())
        except ValueError:
            print(resp.text)

    return None