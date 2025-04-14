from cli.menu.commercial import commercial_menu
from cli.menu.gestion import gestion_menu  # ✅ Ajoute ceci


def show_menu(user, token):
    role = user['role']

    if role == 'COMMERCIAL':
        commercial_menu(user, token)
    elif role == 'GESTION':
        gestion_menu(user, token)
    else:
        print("❌ Rôle non reconnu :", role)