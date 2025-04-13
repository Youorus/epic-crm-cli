from cli.forms.client_form import create_client_form


def commercial_menu(token):
    while True:
        print("\n--- MENU COMMERCIAL ---")
        print("1. Lister mes clients")
        print("2. Créer un client")
        print("3. Modifier un client")
        print("4. Lister mes contrats")
        print("5. Filtrer contrats non signés")
        print("6. Filtrer contrats non payés")
        print("7. Modifier un contrat")
        print("8. Créer un événement")
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
            update_contract(token)
        elif choice == '8':
            data = event_form(token)
            if data:
                create_event(token, data)
        elif choice == '0':
            break
        else:
            print("❌ Choix invalide.")