import re
from datetime import datetime

import requests

from cli.validators import ValidationError, validate_email

API_BASE_URL = "http://127.0.0.1:8000/api/"
CLIENT_URL = API_BASE_URL + "clients/"
CONTRACT_URL = API_BASE_URL + "contracts/"
EVENT_URL = API_BASE_URL + "events/"

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
            create_client(token)
        elif choice == '3':
            update_client(token)
        elif choice == '4':
            list_contracts(token)
        elif choice == '5':
            list_contracts(token, filters="?is_signed=false")
        elif choice == '6':
            list_contracts(token, filters="?amount_due__gt=0")
        elif choice == '7':
            update_contract(token)
        elif choice == '8':
            create_event(token)
        elif choice == '0':
            break
        else:
            print("❌ Choix invalide.")

def validate_phone(phone):
    if not re.match(r"^\+?\d{9,15}$", phone):
        raise ValidationError("Le numéro de téléphone doit contenir entre 9 et 15 chiffres.")

def validate_phone(phone):
    # Accepte : 06 12 34 56 78, +33 6 12 34 56 78, 0612345678, +33612345678
    pattern = r"^(?:\+33\s?|0)[1-9](?:\s?\d{2}){4}$"
    if not re.match(pattern, phone):
        raise ValidationError("Numéro de téléphone invalide (ex: 06 12 34 56 78 ou +33 6 12 34 56 78)")

def parse_french_date(date_str):
    try:
        return datetime.strptime(date_str, "%d %B %Y").date()
    except ValueError:
        raise ValidationError("Format de date invalide. Utilise : 18 avril 2021")

def create_client(token):
    print("\n=== Création d’un client ===")
    headers = {'Authorization': f'Bearer {token}'}

    while True:
        full_name = input("Nom complet : ").strip()
        if full_name.lower() == 'retour':
            return
        if full_name:
            break
        print("❌ Le nom complet est requis.")

    while True:
        email = input("Email : ").strip()
        if email.lower() == 'retour':
            return
        try:
            validate_email(email)
            break
        except ValidationError:
            print("❌ Email invalide.")

    while True:
        phone = input("Téléphone (ex: 06 12 34 56 78 ou +33 6 12 34 56 78) : ").strip()
        if phone.lower() == 'retour':
            return
        try:
            validate_phone(phone)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    while True:
        company_name = input("Nom de l’entreprise : ").strip()
        if company_name.lower() == 'retour':
            return
        if company_name:
            break
        print("❌ Le nom de l’entreprise est requis.")

    while True:
        try:
            last_contact_str = input("Dernier contact [ex: 29 mars 2023] : ").strip()
            if last_contact_str.lower() == 'retour':
                return
            last_contact = parse_french_date(last_contact_str)
            break
        except ValidationError as e:
            print(f"❌ {e}")

    data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "company_name": company_name,
        "last_contact": str(last_contact)
        # date_created géré automatiquement par l'API
        # sales_contact assigné automatiquement via l'utilisateur connecté
    }

    try:
        response = requests.post(CLIENT_URL, json=data, headers=headers)
        if response.status_code == 201:
            print("✅ Client créé avec succès !")
        else:
            print("❌ Erreurs lors de la création :")
            for field, messages in response.json().items():
                print(f" - {field}: {messages}")
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")


def update_client(token):
    print("\n=== Modification d’un client ===")
    headers = {'Authorization': f'Bearer {token}'}
    client_id = input("ID du client à modifier : ").strip()

    full_name = input("Nom complet : ").strip()
    email = input("Email : ").strip()
    phone = input("Téléphone : ").strip()
    company_name = input("Entreprise : ").strip()
    last_contact = input("Dernier contact (YYYY-MM-DD) : ").strip()

    data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "company_name": company_name,
        "last_contact": last_contact
    }

    response = requests.put(f"{CLIENT_URL}{client_id}/", json=data, headers=headers)
    if response.status_code == 200:
        print("✅ Client mis à jour")
    else:
        print("❌ Erreur : ", response.json())


def list_contracts(token, filters=""):
    print("\n--- Liste des contrats ---")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(CONTRACT_URL + filters, headers=headers)
    if response.status_code == 200:
        contrats = response.json()
        for c in contrats:
            print(f"Contrat {c['id']} | Client ID: {c['client']} | Signé: {c['is_signed']} | Restant dû: {c['amount_due']}")
    else:
        print("❌ Erreur :", response.json())


def update_contract(token):
    print("\n=== Modification d’un contrat ===")
    headers = {'Authorization': f'Bearer {token}'}
    contract_id = input("ID du contrat à modifier : ").strip()

    total_amount = input("Montant total : ").strip()
    amount_due = input("Montant dû : ").strip()
    is_signed = input("Contrat signé ? (true/false) : ").strip().lower() == "true"

    data = {
        "total_amount": total_amount,
        "amount_due": amount_due,
        "is_signed": is_signed
    }

    response = requests.put(f"{CONTRACT_URL}{contract_id}/", json=data, headers=headers)
    if response.status_code == 200:
        print("✅ Contrat mis à jour")
    else:
        print("❌ Erreur :", response.json())

def list_clients(token):
    print("\n--- Liste des clients ---")
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(CLIENT_URL, headers=headers)
        if response.status_code == 200:
            clients = response.json()
            for c in clients:
                print(f"{c['id']}: {c['full_name']} - {c['company_name']} - {c['email']}")
        else:
            print("❌ Erreur lors de la récupération des clients.")
    except requests.exceptions.RequestException:
        print("❌ Le serveur est injoignable.")

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