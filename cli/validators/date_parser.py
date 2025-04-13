import dateparser
from cli.validators.exceptions import ValidationError

def parse_french_date(date_str: str):
    date = dateparser.parse(date_str, languages=['fr'])
    if date is None:
        raise ValidationError("Format de date invalide. Utilise : 18 avril 2021")
    return date.date()