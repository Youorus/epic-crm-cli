# cli/menus/gestion_menu.py

from typing import Optional

from cli.forms.contracts.contract_update_form import create_contract_form
# ✅ Imports formulaires (création / mise à jour / suppression utilisateurs & contrats)
from cli.forms.contracts.update_contract_form import update_contract_form
from cli.forms.users.create_user_form import create_user_form
from cli.forms.users.user_update_form import update_user_form
from cli.forms.users.user_delete_form import delete_user_form

# ✅ Imports services (listings + MAJ support événement)
from cli.services.clients.get_clients import list_clients
from cli.services.contracts.get_contracts import list_contracts
from cli.services.events.get_events import list_events
from cli.services.events.update_support_event import update_support_event

# ✅ Session & URLs
from cli.utils.session import session
from cli.utils.config import EVENT_URL


def gestion_menu() -> Optional[None]:
    """
    Affiche le menu principal pour un utilisateur au rôle GESTION.

    Fonctions disponibles :
      1) Lister tous les clients
      2) Lister tous les contrats
      3) Créer un contrat
      4) Modifier un contrat (saisie d’un ID)
      5) Lister tous les événements
      6) Lister uniquement les événements sans support (filtre serveur)
      7) Assigner un support à un événement (formulaire → PATCH)
      8) Créer un collaborateur
      9) Modifier un collaborateur
     10) Supprimer un collaborateur
      0) Retour au routeur de menus

    Remarques :
    - Tous les appels réseau passent par `session` (JWT géré automatiquement).
    - Les filtres sont délégués au backend (django-filter), via `params={...}`.
    - On conserve l’UX et la logique existantes (pas de rupture).
    """
    while True:
        # ─────────────────────────────────────────────────────────
        # Affichage du menu
        # ─────────────────────────────────────────────────────────
        print("\n" + "=" * 50)
        print("🧭 MENU GESTION".center(50))
        print("=" * 50)
        print("1. Lister tous les clients")
        print("2. Lister tous les contrats")
        print("3. Créer un contrat")
        print("4. Modifier un contrat")
        print("5. Lister tous les événements")
        print("6. Filtrer événements sans support")
        print("7. Modifier un événement (assigner support)")
        print("8. Créer un collaborateur")
        print("9. Modifier un collaborateur")
        print("10. Supprimer un collaborateur")
        print("0. Retour")

        choice = input("\nVotre choix : ").strip()

        # ─────────────────────────────────────────────────────────
        # 1) Clients
        # ─────────────────────────────────────────────────────────
        if choice == "1":
            list_clients(display=True)

        # ─────────────────────────────────────────────────────────
        # 2) Contrats
        # ─────────────────────────────────────────────────────────
        elif choice == "2":
            list_contracts(display=True)

        # ─────────────────────────────────────────────────────────
        # 3) Créer un contrat (la form gère validation + POST)
        # ─────────────────────────────────────────────────────────
        elif choice == "3":
            create_contract_form()

        # ─────────────────────────────────────────────────────────
        # 4) Modifier un contrat (saisie et validation basique de l’ID)
        # ─────────────────────────────────────────────────────────
        elif choice == "4":
            while True:
                cid = input("ID du contrat à modifier (ou 'retour') : ").strip()
                if cid.lower() == "retour":
                    break
                if cid.isdigit():
                    update_contract_form(int(cid))  # la form PATCH directement
                    break
                print("❌ L’ID doit être un entier.")

        # ─────────────────────────────────────────────────────────
        # 5) Événements (liste complète)
        # ─────────────────────────────────────────────────────────
        elif choice == "5":
            list_events(display=True)

        # ─────────────────────────────────────────────────────────
        # 6) Événements sans support (filtre serveur)
        # ─────────────────────────────────────────────────────────
        elif choice == "6":
            list_events(params={"support_contact__isnull": "true"}, display=True)

        # ─────────────────────────────────────────────────────────
        # 7) Assigner un support à un événement
        #    - Le formulaire renvoie (event_id, payload)
        #    - PATCH direct via la session
        # ─────────────────────────────────────────────────────────
        elif choice == "7":
            event_id, payload = update_support_event()
            if event_id and payload:
                # Utilise l’URL configurée (évite les chemins en dur)
                resp = session.patch(f"{EVENT_URL}{event_id}/", json=payload)
                if 200 <= resp.status_code < 300:
                    print(f"✅ Support assigné à l’événement #{event_id}.")
                else:
                    # Affichage d’erreur lisible
                    try:
                        print("❌ Erreur :", resp.status_code, resp.json())
                    except ValueError:
                        print("❌ Erreur :", resp.status_code, resp.text)

        # ─────────────────────────────────────────────────────────
        # 8) Utilisateurs : création
        # ─────────────────────────────────────────────────────────
        elif choice == "8":
            create_user_form()  # POST direct

        # ─────────────────────────────────────────────────────────
        # 9) Utilisateurs : modification
        # ─────────────────────────────────────────────────────────
        elif choice == "9":
            update_user_form()  # PATCH direct

        # ─────────────────────────────────────────────────────────
        # 10) Utilisateurs : suppression
        # ─────────────────────────────────────────────────────────
        elif choice == "10":
            delete_user_form()  # DELETE direct

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