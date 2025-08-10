from datetime import datetime
from typing import Any, Dict, List, Optional

def _fmt_euro(val) -> str:
    try:
        return f"{float(val):,.2f} €".replace(",", " ").replace(".", ",")
    except (TypeError, ValueError):
        return "—"


def _date_only(value: Optional[str]) -> str:
    if not value:
        return "—"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except Exception:
        return value[:10]