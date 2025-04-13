# cli/validators/password_validator.py
from .exceptions import ValidationError

def validate_password(password: str):
    if len(password) < 8:
        raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")