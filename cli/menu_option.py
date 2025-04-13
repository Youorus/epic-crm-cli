from cli.menu.commercial import commercial_menu


def show_menu(user, token):
    role = user['role']
    if role == 'COMMERCIAL':
        commercial_menu(user,token)
    else:
        print("❌ Rôle non reconnu :", role)