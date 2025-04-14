# cli/menu/gestion.py
from cli.forms.contract_update_form import create_contract_form
from cli.forms.update_contract_form import update_contract_form
from cli.forms.update_event_form import update_event_form
from cli.forms.user_create_form import create_user_form
from cli.forms.user_delete_form import delete_user_form
from cli.forms.user_update_form import update_user_form
from cli.services.delete_user import delete_user
from cli.services.get_clients import list_clients
from cli.services.get_contracts import list_contracts
from cli.services.get_events import list_events
from cli.services.update_contract import update_contract
from cli.services.update_event import update_event
from cli.services.create_contract import create_contract
from cli.services.update_user import update_user
from cli.services.user import create_user


def gestion_menu(user, token):
    while True:
        print("\n--- MENU GESTION ---")
        print("1. Lister tous les clients")
        print("2. Lister tous les contrats")
        print("3. Créer un contrat")
        print("4. Modifier un contrat")
        print("5. Lister tous les événements")
        print("6. Filtrer événements sans support")
        print("7. Modifier un événement")
        print("8. Créer un collaborateur")
        print("9. Modifier un collaborateur")
        print("10. Supprimer un collaborateur")
        print("0. Quitter")
        choice = input("Choix : ")

        if choice == '1':
            list_clients(token)

        elif choice == '2':
            list_contracts(token)

        elif choice == '3':
            data = create_contract_form()
            create_contract(token, data)

        elif choice == '4':
            contract_id, data = update_contract_form()
            update_contract(token, contract_id, data)

        elif choice == '5':
            list_events(token)

        elif choice == '6':
            list_events(token, filters="?support_contact__isnull=true")

        elif choice == '7':
            event_id, data = update_event_form()
            update_event(token, event_id, data)

        elif choice == '8':
            data = create_user_form()
            create_user(token, data)

        elif choice == '9':
            user_id, data = update_user_form()
            update_user(token, user_id, data)

        elif choice == '10':
            user_id = delete_user_form()
            delete_user(token, user_id)

        elif choice == '0':
            break

        else:
            print("❌ Choix invalide.")