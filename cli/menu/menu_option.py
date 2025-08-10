# cli/menus/menu_router.py
from cli.menu.commercial import commercial_menu
from cli.menu.gestion import gestion_menu
from cli.menu.support import support_menu
from cli.utils.session import session


def show_menu() -> None:
    """
    Routeur principal des menus CLI selon le rôle de l'utilisateur connecté.

    🔹 Utilise la session globale (`session.user`) pour déterminer le rôle.
    🔹 Redirige vers le menu correspondant :
        - GESTION     → gestion_menu()
        - COMMERCIAL  → commercial_menu()
        - SUPPORT     → support_menu()
    🔹 Si aucun utilisateur n'est connecté ou rôle inconnu → message d'erreur.

    Notes :
    - `session.user` est défini après authentification réussie.
    - La structure des menus est indépendante, ce routeur se contente
      d'appeler la bonne fonction.
    """
    # Vérification utilisateur connecté
    if not session.user:
        print("❌ Aucun utilisateur connecté. Veuillez vous authentifier.")
        return

    # Récupération du rôle
    role = session.user.get("role")

    # Dispatch vers le menu correspondant
    if role == "GESTION":
        gestion_menu()
    elif role == "COMMERCIAL":
        commercial_menu()
    elif role == "SUPPORT":
        support_menu()
    else:
        print(f"❌ Rôle non reconnu ou non autorisé : {role}")