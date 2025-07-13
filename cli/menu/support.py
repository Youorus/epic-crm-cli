from cli.services.get_events import list_events
from cli.services.update_event import update_event
from cli.forms.update_event_form import update_event_form


def support_menu(user, token):
    while True:
        print("\n--- MENU SUPPORT ---")
        print("1. Voir mes événements")
        print("2. Modifier un de mes événements")
        print("0. Quitter")
        choice = input("Choix : ")

        # 📅 Lister les événements assignés à ce support
        if choice == '1':
            list_events(token, user_id=user['id'])  # ✅ user_id géré côté service

        # 🛠️ Modifier un événement (avec vérification d’autorisation dans le form)
        elif choice == '2':
            event_id, data = update_event_form(token, user)
            if event_id and data:
                update_event(token, event_id, data)

        elif choice == '0':
            break
        else:
            print("❌ Choix invalide.")