# cli/menus/commercial_menu.py

from typing import Optional

from cli.services.clients.get_clients import list_clients
from cli.services.contracts.get_contracts import list_contracts
from cli.forms.clients.create_client_form import create_client_form
from cli.forms.clients.update_client_form import update_client_form
from cli.forms.events.create_event_form import create_event_form


def commercial_menu() -> Optional[None]:
    """
    Affiche le menu principal pour un utilisateur au rôle COMMERCIAL.

    Comportement :
      1) Lister les clients du commercial (restriction côté API).
      2) Créer un client (formulaire → POST direct).
      3) Mettre à jour l’un de ses clients (formulaire → PATCH direct).
      4) Lister les contrats (restriction par rôle côté API).
      5) Lister uniquement les contrats non signés (filtre serveur).
      6) Lister les contrats avec montant dû > 0 (filtre serveur).
      7) Créer un événement pour un contrat signé (formulaire → POST direct).
      0) Retour au routeur de menus.

    Retour :
      - None (fonction purement interactive).
    """
    while True:
        # ─────────────────────────────────────────────────────────
        # Affichage du menu
        # ─────────────────────────────────────────────────────────
        print("\n" + "=" * 50)
        print("🧭 MENU COMMERCIAL".center(50))
        print("=" * 50)
        print("1. Lister mes clients")
        print("2. Créer un client")
        print("3. Mettre à jour un de mes clients")
        print("4. Lister mes contrats")
        print("5. Contrats non signés")
        print("6. Modifier un de mes contrats")
        print("7. Créer un événement (pour un contrat signé)")
        print("0. Retour")

        choice = input("\nVotre choix : ").strip()

        # ─────────────────────────────────────────────────────────
        # 1) Lister les clients du commercial (backend restreint par rôle)
        # ─────────────────────────────────────────────────────────
        if choice == "1":
            list_clients(display=True)

        # ─────────────────────────────────────────────────────────
        # 2) Créer un client (la form gère validation + POST)
        # ─────────────────────────────────────────────────────────
        elif choice == "2":
            create_client_form()

        # ─────────────────────────────────────────────────────────
        # 3) Mettre à jour un client (saisie de l’ID, validation basique)
        # ─────────────────────────────────────────────────────────
        elif choice == "3":
            cid = input("ID du client à modifier (ou 'retour') : ").strip()
            if cid.lower() != "retour" and cid.isdigit():
                update_client_form(int(cid))
            elif cid.lower() != "retour":
                print("❌ L’ID doit être un entier.")

        # ─────────────────────────────────────────────────────────
        # 4) Lister les contrats (restriction par rôle côté API)
        # ─────────────────────────────────────────────────────────
        elif choice == "4":
            list_contracts(display=True)

        # ─────────────────────────────────────────────────────────
        # 5) Contrats non signés (filtre serveur : ?is_signed=false)
        # ─────────────────────────────────────────────────────────
        elif choice == "5":
            list_contracts(params={"is_signed": "false"}, display=True)

        # ─────────────────────────────────────────────────────────
        # 6) Contrats avec montant dû > 0 (filtre serveur)
        # ─────────────────────────────────────────────────────────
        elif choice == "6":
            list_contracts(params={"amount_due__gt": "0"}, display=True)

        # ─────────────────────────────────────────────────────────
        # 7) Créer un événement pour un contrat signé :
        #    - Récupère la liste des contrats signés (filtre serveur),
        #    - Passe cette liste au formulaire, qui POST directement l’événement.
        # ─────────────────────────────────────────────────────────
        elif choice == "7":
            signed_contracts = list_contracts(params={"is_signed": "true"}, display=False)
            if not signed_contracts:
                print("ℹ️ Aucun contrat signé disponible.")
                continue
            create_event_form(signed_contracts)

        # ─────────────────────────────────────────────────────────
        # 0) Retour
        # ─────────────────────────────────────────────────────────
        elif choice == "0":
            return None

        # ─────────────────────────────────────────────────────────
        # Choix invalide
        # ─────────────────────────────────────────────────────────
        else:
            print("❌ Choix invalide. Réessayez.")