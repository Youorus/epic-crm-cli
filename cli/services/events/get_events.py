# cli/services/get_events.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from cli.utils.config import EVENT_URL
from cli.utils.session import session


def _date_dt(value: Optional[str]) -> str:
    if not value:
        return "—"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return value


def _clip(val: Any, width: int) -> str:
    s = "" if val is None else str(val)
    return (s[: width - 1] + "…") if len(s) > width else s


def list_events(
    params: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
    display: bool = True,
    as_table: bool = True,
    mine_only_for_support: bool = False,   # <-- nouveau
) -> List[Dict[str, Any]]:
    """
    Liste les événements depuis l'API.

    - Filtrage côté backend via `params` (ex: {"support_contact__isnull": "true"})
    - `user_id` force support_contact=<id>
    - `mine_only_for_support=True` utilise l'id de l'utilisateur connecté si son rôle est SUPPORT
    - Gère pagination DRF ({count,next,previous,results})
    - Affichage tableau (par défaut) ou détaillé
    """
    q: Dict[str, Any] = dict(params or {})

    # Si on veut "mes événements" pour un support, on impose le filtre
    if mine_only_for_support and session.user and session.user.get("role") == "SUPPORT":
        q["support_contact"] = session.user["id"]

    # Si user_id explicite passé, il a priorité
    if user_id is not None:
        q["support_contact"] = user_id

    resp = session.get(EVENT_URL, params=q)
    data = session.ok_json(resp)
    if data is None:
        return []

    # Pagination DRF
    if isinstance(data, dict) and "results" in data:
        items = data.get("results", []) or []
        count = data.get("count")
        next_page = data.get("next")
        prev_page = data.get("previous")
        paginated = True
    else:
        items = data or []
        count = len(items)
        next_page = prev_page = None
        paginated = False

    if not items:
        if display:
            print("🔍 Aucun événement trouvé.")
        return []

    if not display:
        return items

    if as_table:
        W_ID, W_NAME, W_CLIENT, W_SUPPORT, W_START, W_END, W_LOC, W_ATT = 5, 24, 22, 16, 16, 16, 18, 6
        header = (
            f"{'ID':<{W_ID}} "
            f"{'Nom':<{W_NAME}} "
            f"{'Client':<{W_CLIENT}} "
            f"{'Support':<{W_SUPPORT}} "
            f"{'Début':<{W_START}} "
            f"{'Fin':<{W_END}} "
            f"{'Lieu':<{W_LOC}} "
            f"{'👥':>{W_ATT}}"
        )
        print("\n📅 === LISTE DES ÉVÉNEMENTS ===")
        print(header)
        print("-" * len(header))

        for e in items:
            client_label = e.get("client_full_name") or e.get("client")
            support_label = e.get("support_contact_username") or e.get("support_contact") or "—"
            start = _date_dt(e.get("event_start"))
            end = _date_dt(e.get("event_end"))
            row = (
                f"{str(e.get('id')):<{W_ID}} "
                f"{_clip(e.get('event_name', 'Sans nom'), W_NAME):<{W_NAME}} "
                f"{_clip(client_label, W_CLIENT):<{W_CLIENT}} "
                f"{_clip(support_label, W_SUPPORT):<{W_SUPPORT}} "
                f"{_clip(start, W_START):<{W_START}} "
                f"{_clip(end, W_END):<{W_END}} "
                f"{_clip(e.get('location', '—'), W_LOC):<{W_LOC}} "
                f"{str(e.get('attendees', '—')):>{W_ATT}}"
            )
            print(row)
    else:
        print("\n📅 === LISTE DES ÉVÉNEMENTS ===")
        for e in items:
            client_label = e.get("client_full_name") or e.get("client")
            support_label = e.get("support_contact_username") or e.get("support_contact") or "— Aucun"
            print("\n" + "-" * 50)
            print(f"🆔 ID Événement  : {e.get('id')}")
            print(f"📛 Nom           : {e.get('event_name', 'Sans nom')}")
            print(f"👤 Client        : {client_label}")
            print(f"🧑‍💼 Support      : {support_label}")
            print(f"📍 Lieu          : {e.get('location', 'Non spécifié')}")
            print(f"👥 Participants  : {e.get('attendees', 'NC')}")
            print(f"🕒 Début         : {_date_dt(e.get('event_start'))}")
            print(f"🕓 Fin           : {_date_dt(e.get('event_end'))}")
            print(f"📝 Notes         : {e.get('notes', 'Aucune note')}")

    if paginated:
        print(
            f"\n📊 Total: {count} | "
            f"⬅️ Page précédente: {'Oui' if prev_page else 'Non'} | "
            f"➡️ Page suivante: {'Oui' if next_page else 'Non'}"
        )

    return items