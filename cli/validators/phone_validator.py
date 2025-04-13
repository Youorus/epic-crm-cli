import re
from .exceptions import ValidationError

def validate_phone(phone: str):
    pattern = r"^(?:\+33\s?|0)[1-9](?:\s?\d{2}){4}$"
    if not re.match(pattern, phone):
        raise ValidationError("Numéro de téléphone invalide (ex: 06 12 34 56 78 ou +33 6 12 34 56 78)")