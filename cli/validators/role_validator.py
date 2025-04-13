# cli/validators/role_validator.py
from .exceptions import ValidationError

def validate_role(role: str):
    valid_roles = ['COMMERCIAL', 'SUPPORT', 'GESTION']
    if role.upper() not in valid_roles:
        raise ValidationError(f"Le rôle doit être l'un de : {', '.join(valid_roles)}.")