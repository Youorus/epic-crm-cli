# cli/forms/user_update_form.py

def update_user_form():
    print("\n=== Modification d’un collaborateur ===")
    user_id = input("ID de l'utilisateur à modifier : ").strip()
    data = {}

    username = input("Nom d'utilisateur (laisser vide pour ne pas changer) : ").strip()
    if username:
        data["username"] = username

    email = input("Email (laisser vide pour ne pas changer) : ").strip()
    if email:
        data["email"] = email

    password = input("Mot de passe (laisser vide pour ne pas changer) : ").strip()
    if password:
        if len(password) < 8:
            print("❌ Le mot de passe doit contenir au moins 8 caractères.")
        else:
            data["password"] = password

    print("Rôles disponibles : COMMERCIAL / SUPPORT / GESTION")
    role = input("Rôle (laisser vide pour ne pas changer) : ").strip().upper()
    if role in ["COMMERCIAL", "SUPPORT", "GESTION"]:
        data["role"] = role
    elif role != "":
        print("❌ Rôle ignoré (invalide)")

    return user_id, data