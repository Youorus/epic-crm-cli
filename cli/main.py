# cli/main.py
import os

from cli.menu.menu_option import show_menu
from cli.utils.session import session

# 1) Config Django AVANT les imports qui en dépendent
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epic_crm.settings")
import django
django.setup()


def _ensure_current_user():
    """
    Si la session n'a pas encore d'utilisateur chargé, on le récupère à partir du token.
    """
    if getattr(session, "user", None):
        return

    try:
        # On lit l'ID dans l'access token puis GET /api/users/{id}/
        import jwt
        access = session._ensure_access() if hasattr(session, "_ensure_access") else session.ensure_access_token()
        payload = jwt.decode(access, options={"verify_signature": False})
        uid = payload.get("user_id")
        if not uid:
            return
        resp = session.get(f"/api/users/{uid}/")
        data = session.ok_json(resp)
        if data:
            session.user = data  # on mémorise pour tout le CLI
    except Exception:
        # Pas bloquant : le menu pourra encore s'afficher, mais sans le nom/role
        pass


def main():
    # 3) Login (username + password -> JWT)
    if not session.login_prompt():
        return

    # 4) S'assurer d'avoir l'utilisateur courant en mémoire
    _ensure_current_user()

    # 5) Petit message d’accueil
    if getattr(session, "user", None):
        print(f"👋 Bonjour {session.user.get('username')} ({session.user.get('role')})")

    # 6) Router vers le menu selon le rôle
    show_menu()


if __name__ == "__main__":
    main()