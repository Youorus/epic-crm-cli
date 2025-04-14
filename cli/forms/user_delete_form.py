def delete_user_form():
    print("\n=== Suppression d’un collaborateur ===")
    user_id = input("ID de l'utilisateur à supprimer : ").strip()

    confirmation = input(f"⚠️ Confirmer la suppression de l’utilisateur {user_id} ? (oui/non) : ").strip().lower()
    if confirmation != "oui":
        print("❌ Suppression annulée.")
        return None

    return user_id