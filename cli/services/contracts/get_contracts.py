from typing import Any, Dict, List, Optional
from cli.services.contracts.helpers import _fmt_euro, _date_only
from cli.utils.config import CONTRACT_URL
from cli.utils.session import session


def list_contracts(params: Optional[Dict[str, Any]] = None, display: bool = True) -> List[Dict[str, Any]]:
    """
    Récupère les contrats via l’API DRF, gère la pagination éventuelle et,
    si demandé, affiche un tableau formaté côté CLI.

    Comportement :
      - Les filtres sont passés au backend via `params` (ex. {"is_signed": "false"}).
      - Retourne toujours une liste d’objets contrats (page courante si pagination).
      - En cas d’erreur HTTP/JSON, retourne une liste vide (les erreurs sont déjà affichées par ok_json()).

    Paramètres :
      params (dict | None) : dictionnaire de query params transmis à l’API.
      display (bool)       : si True, affiche le tableau des contrats.

    Retour :
      list[dict] : liste des contrats.
    """
    # ── Appel API (session gère JWT + headers)
    resp = session.get(CONTRACT_URL, params=params or {})
    data = session.ok_json(resp)
    if data is None:
        return []

    # ── Gestion pagination DRF ({count,next,previous,results}) ou liste simple
    if isinstance(data, dict) and "results" in data:
        items: List[Dict[str, Any]] = data.get("results", [])
        count: Optional[int] = data.get("count")
        next_page: Optional[str] = data.get("next")
        previous_page: Optional[str] = data.get("previous")
        paginated: bool = True
    else:
        items = data  # type: ignore[assignment]
        count = None
        next_page = None
        previous_page = None
        paginated = False

    # ── Aucun résultat
    if not items:
        if display:
            print("🔍 Aucun contrat trouvé.")
        return []

    # ── Affichage tableau (optionnel)
    if display:
        print("\n--- Liste des contrats ---")
        header = (
            f"{'ID':<5} {'Client':<25} {'Commercial':<15} "
            f"{'Total':>12} {'Payé':>12} {'Restant':>12} {'Signé':<7} {'Créé le':<10}"
        )
        print(header)
        print("-" * len(header))

        for c in items:
            # Sécurise les montants et calcule “payé”
            total_f = float(c.get("total_amount") or 0)
            due_f = float(c.get("amount_due") or 0)
            paid_f = max(total_f - due_f, 0.0)

            # Étiquettes lisibles (fallbacks robustes)
            client_label = c.get("client_full_name") or str(c.get("client") or "N/A")
            sales_contact = c.get("sales_contact_username") or "Non assigné"

            # Ligne formatée
            print(
                f"{c['id']:<5} {client_label:<25} {sales_contact:<15} "
                f"{_fmt_euro(total_f):>12} {_fmt_euro(paid_f):>12} {_fmt_euro(due_f):>12} "
                f"{'✅' if c.get('is_signed') else '❌':<7} "
                f"{_date_only(c.get('created_at') or c.get('date_created')):<10}"
            )

        # Pied de tableau si pagination DRF active
        if paginated:
            print(
                f"\nTotal: {count} | "
                f"Page précédente: {'Oui' if previous_page else 'Non'} | "
                f"Page suivante: {'Oui' if next_page else 'Non'}"
            )

    return items