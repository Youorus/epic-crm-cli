


def create_event(token):
    print("\n=== Création d’un événement ===")
    print("(Tape 'retour' à tout moment pour revenir au menu)")

    headers = {'Authorization': f'Bearer {token}'}

    try:
        # Afficher les contrats signés disponibles
        response = requests.get(CONTRACT_URL + "?is_signed=true", headers=headers)
        if response.status_code != 200:
            print("❌ Impossible de récupérer les contrats signés.")
            return

        contrats = response.json()
        if not contrats:
            print("⚠️ Aucun contrat signé disponible.")
            return

        print("\nContrats disponibles :")
        for contrat in contrats:
            print(f"{contrat['id']}: Client ID {contrat['client']} - Montant total: {contrat['total_amount']}")

        contract_id = input("ID du contrat pour l'événement : ").strip()
        if contract_id.lower() == "retour":
            return

        event_name = input("Nom de l'événement : ").strip()
        if event_name.lower() == "retour":
            return

        location = input("Lieu : ").strip()
        if location.lower() == "retour":
            return

        attendees = input("Nombre de participants : ").strip()
        if attendees.lower() == "retour":
            return

        start = input("Date/heure de début (YYYY-MM-DD HH:MM) : ").strip()
        if start.lower() == "retour":
            return

        end = input("Date/heure de fin (YYYY-MM-DD HH:MM) : ").strip()
        if end.lower() == "retour":
            return

        notes = input("Notes (facultatif) : ").strip()

        # Création de l'événement
        data = {
            "contract": int(contract_id),
            "client": None,  # sera déterminé depuis le contrat si possible
            "event_name": event_name,
            "location": location,
            "attendees": int(attendees),
            "event_start": start,
            "event_end": end,
            "notes": notes,
        }

        # Récupérer le client automatiquement depuis le contrat
        contrat_data = next((c for c in contrats if str(c['id']) == contract_id), None)
        if not contrat_data:
            print("❌ Contrat introuvable.")
            return
        data["client"] = contrat_data["client"]

        response = requests.post(EVENT_URL, json=data, headers=headers)
        if response.status_code == 201:
            print("🎉 Événement créé avec succès !")
        else:
            print("❌ Erreur lors de la création de l’événement :")
            print(response.json())

    except requests.exceptions.RequestException:
        print("❌ Erreur réseau.")