# cli/validators/username_validator.py
from .exceptions import ValidationError

def validate_username(username: str):
    if not username.strip():
        raise ValidationError("Le nom d'utilisateur est requis.")