import dateparser
import re
from datetime import datetime
from cli.validators.exceptions import ValidationError

def parse_french_datetime(date_str: str) -> datetime:
    """
    Transforme une date en français comme '29 mai 2025 à 18h' → datetime
    """
    # Nettoyage : "à 18h" → "18:00"
    cleaned = re.sub(r'à\s*(\d{1,2})h', r'\1:00', date_str.strip(), flags=re.IGNORECASE)
    # Ex : "29 mai 2025 à 18h" → "29 mai 2025 18:00"

    date = dateparser.parse(cleaned, languages=['fr'])
    if not date:
        raise ValidationError("Format de date invalide. Exemple : '18 avril 2025 à 14h'")
    return date

def validate_event_dates(start_str: str, end_str: str) -> tuple[datetime, datetime]:
    start = parse_french_datetime(start_str)
    end = parse_french_datetime(end_str)
    now = datetime.now()

    if start < now:
        raise ValidationError("La date de début ne peut pas être dans le passé.")

    if end <= start:
        raise ValidationError("La date de fin doit être postérieure à la date de début.")

    return start, end