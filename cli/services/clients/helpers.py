# ----------- Helpers d'affichage -----------
from datetime import datetime
from typing import List, Dict, Tuple, Any

def _parse_date(value: str | None) -> str:
    """Retourne une date lisible (YYYY-MM-DD) à partir d'un ISO datetime/date string."""
    if not value:
        return "—"
    try:
        # Essaie datetime d'abord
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        # Fallback : tronque (date-only ou format inconnu)
        return value[:10]


def _fit(text: Any, width: int) -> str:
    s = str(text) if text is not None else "—"
    if len(s) <= width:
        return s.ljust(width)
    return s[: max(0, width - 1)] + "…"


def _print_table(headers: List[Tuple[str, int]], rows: List[List[Any]], footer: str | None = None) -> None:
    """Affiche un tableau simple, lisible en CLI, avec largeurs fixes."""
    # Ligne d'en-tête
    header_line = " | ".join(_fit(h, w) for h, w in headers)
    sep = "-+-".join("-" * w for _, w in headers)
    print("\n" + header_line)
    print(sep)

    # Lignes
    for r in rows:
        print(" | ".join(_fit(val, headers[i][1]) for i, val in enumerate(r)))

    if footer:
        print("\n" + footer)