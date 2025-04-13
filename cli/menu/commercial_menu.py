# cli/menu/commercial_menu.py
from cli.forms.contract_update_form import update_contract_form
from cli.forms.create_client_form import create_client_form
from cli.forms.create_event_form import create_event_form
from cli.forms.update_client_form import update_client_form
from cli.forms.update_event_form import update_event_form
from cli.services.create_client import create_client
from cli.services.create_event import create_event
from cli.services.get_clients import list_clients
from cli.services.get_contracts import list_contracts
from cli.services.update_client import update_client
from cli.services.update_contract import update_contract
from cli.services.update_event import update_event


def commercial_menu(token):
    while True:
        print("\n--- MENU COMMERCIAL ---")
        print("1. Lister des clients")
        print("2. Créer un client")
        print("3. Modifier un client")
        print("4. Lister mes contrats")
        print("5. Filtrer contrats non signés")
        print("6. Filtrer contrats non payés")
        print("7. Modifier un contrat")
        print("8. Créer un événement")
        print("9. Modifier un événement")
        print("0. Quitter")
        choice = input("Choix : ")

        if choice == '1':
            list_clients(token)

        elif choice == '2':
            data = create_client_form()
            create_client(token, data)

        elif choice == '3':
            client_id, data = update_client_form()
            update_client(token, client_id, data)

        elif choice == '4':
            list_contracts(token)

        elif choice == '5':
            list_contracts(token, filters="?is_signed=false")

        elif choice == '6':
            list_contracts(token, filters="?amount_due__gt=0")

        elif choice == '7':
            contract_id, data = update_contract_form()
            update_contract(token, contract_id, data)

        elif choice == '8':
            signed_contracts = list_contracts(token, filters="?is_signed=true", display=False)
            data = create_event_form(signed_contracts)
            if data:
                create_event(token, data)

        elif choice == '9':
            event_id, data = update_event_form()
            update_event(token, event_id, data)

        elif choice == '0':
            break

        else:
            print("❌ Choix invalide.")