# cli/menus/support_menu.py
"""
Menu CLI pour le rôle SUPPORT.

Fonctions principales :
- Lister uniquement les événements assignés à l'utilisateur connecté.
- Mettre à jour un événement dont l'utilisateur est responsable.
Le backend (permissions) garantit que le support ne peut modifier
que ses propres événements.
"""

from cli.services.events.get_events import list_events
from cli.services.events.update_event import _input_int, _update_event_form_support
from cli.utils.config import EVENT_URL
from cli.utils.session import session


def support_menu() -> None:
    """
    Affiche le menu dédié au rôle SUPPORT et route les actions.
    - Option 1 : liste les événements dont `support_contact` = session.user.id
    - Option 2 : met à jour un événement (horaires, notes, etc.) si autorisé
    """
    while True:
        print("\n" + "=" * 50)
        print("🧭 MENU SUPPORT".center(50))
        print("=" * 50)
        print("1. Lister MES événements (assignés à moi)")
        print("2. Mettre à jour un de MES événements")
        print("0. Retour")

        choice = input("\nVotre choix : ").strip()

        if choice == "1":
            # Filtrage 100% côté backend : on passe le paramètre support_contact=<id>
            # NB : list_events(params=...) est la signature actuelle.
            if not session.user:
                print("❌ Utilisateur non connecté.")
                continue

            list_events(
                params={"support_contact": session.user["id"]},
                display=True,
                as_table=True,
            )

        elif choice == "2":
            # Saisie sécurisée d'un entier (ou 'retour' pour annuler)
            event_id = _input_int("ID de l’événement à modifier (ou 'retour') : ")
            if event_id is None:
                continue

            # Le formulaire renvoie un payload prêt à être PATCHé (ou None si annulé)
            payload = _update_event_form_support(event_id)
            if not payload:
                continue

            # PATCH → Le backend vérifiera que cet événement est bien assigné à ce support
            resp = session.patch(f"{EVENT_URL}{event_id}/", json=payload)
            if 200 <= resp.status_code < 300:
                print("✅ Événement mis à jour.")
            else:
                print(f"❌ Erreur ({resp.status_code})")
                try:
                    print("📨", resp.json())
                except ValueError:
                    print("📨", resp.text)

        elif choice == "0":
            break

        else:
            print("❌ Choix invalide. Réessayez.")