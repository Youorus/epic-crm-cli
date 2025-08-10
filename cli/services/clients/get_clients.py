from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional

from cli.services.clients.helpers import _parse_date, _print_table
from cli.utils.config import CLIENT_URL
from cli.utils.session import session


def list_clients(display: bool = True) -> list[dict]:
    """
    Récupère les clients via l’API (DRF), gère la pagination éventuelle et,
    si demandé, affiche un tableau formaté côté CLI.

    Comportement :
      - Retourne toujours une liste d’objets clients (items), même si l’API est paginée.
      - N’affiche rien si `display=False`.
      - En cas d’erreur HTTP ou JSON invalide, retourne une liste vide.

    Paramètres :
      display (bool) : si True, affiche un tableau des clients.

    Retour :
      list[dict] : liste des clients (page courante si pagination DRF).
    """
    # ── Appel API (session gère JWT + headers)
    resp = session.get(CLIENT_URL)
    data = session.ok_json(resp)
    if data is None:
        # Erreur déjà journalisée par ok_json()
        return []

    # ── Gestion pagination DRF ({count,next,previous,results}) ou liste simple
    if isinstance(data, dict) and "results" in data:
        items: List[Dict[str, Any]] = data.get("results", [])
        count: Optional[int] = data.get("count")
        next_page: Optional[str] = data.get("next")
        previous_page: Optional[str] = data.get("previous")
        is_paginated: bool = True
    else:
        items = data  # type: ignore[assignment]
        count = len(items) if isinstance(items, list) else 0
        next_page = None
        previous_page = None
        is_paginated = False

    # ── Aucun résultat
    if not items:
        if display:
            print("🔍 Aucun client trouvé.")
        return []

    # ── Affichage tableau (optionnel)
    if display:
        # Définition des colonnes (titre, largeur)
        headers: List[Tuple[str, int]] = [
            ("ID", 4),
            ("Nom complet", 24),
            ("Entreprise", 22),
            ("Email", 28),
            ("Téléphone", 14),
            ("Commercial", 18),
            ("Dernier contact", 14),
            ("Créé le", 10),
        ]

        # Préparation des lignes à afficher
        rows: List[List[Any]] = []
        for c in items:
            rows.append([
                c.get("id"),
                c.get("full_name"),
                c.get("company_name"),
                c.get("email"),
                c.get("phone"),
                # Selon le serializer côté API, ce champ est exposé comme `sales_contact_username`
                c.get("sales_contact_username") or "Non assigné",
                _parse_date(c.get("last_contact")),
                _parse_date(c.get("created_at")),
            ])

        # Pied de tableau si pagination DRF active
        footer: Optional[str] = None
        if is_paginated:
            footer = (
                f"Total: {count} | "
                f"Page précédente: {'Oui' if previous_page else 'Non'} | "
                f"Page suivante: {'Oui' if next_page else 'Non'}"
            )

        # Impression du tableau via helper dédié
        _print_table(headers, rows, footer)

    return items