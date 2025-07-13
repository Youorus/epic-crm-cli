from cli.menu.commercial import commercial_menu
from cli.menu.gestion import gestion_menu
from cli.menu.support import support_menu  # Ajout du menu support

def show_menu(user, token):
    role = user['role']

    if role == 'COMMERCIAL':
        commercial_menu(user, token)

    elif role == 'GESTION':
        gestion_menu(user, token)

    elif role == 'SUPPORT':
        support_menu(user, token)  # Appel du menu support

    else:
        print("❌ Rôle non reconnu :", role)