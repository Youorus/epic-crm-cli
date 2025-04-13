from .commercial import commercial_menu
from .gestion import gestion_menu



def show_menu(user, token):
    role = user['role']

    if role == 'GESTION':
        gestion_menu(token)
    elif role == 'COMMERCIAL':
        commercial_menu(token)
    else:
        print("❌ Rôle non reconnu :", role)