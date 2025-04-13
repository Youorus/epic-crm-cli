from datetime import datetime
from .exceptions import ValidationError

def parse_french_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%d %B %Y").date()
    except ValueError:
        raise ValidationError("Format de date invalide. Utilise : 18 avril 2021")