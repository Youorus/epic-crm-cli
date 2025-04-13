from cli.auth import login, get_current_user
from cli.menu import show_menu

def main():
    token = login()
    if not token:
        return

    user = get_current_user(token)
    if not user:
        print("❌ Utilisateur introuvable")
        return

    print(f"👤 Connecté en tant que {user['username']} ({user['role']})")
    show_menu(user, token)

if __name__ == '__main__':
    main()