import re

class ValidationError(Exception):
    """Exception levée lorsqu'une entrée utilisateur est invalide."""
    pass

def validate_username(username: str):
    if not username.strip():
        raise ValidationError("Le nom d'utilisateur est requis.")

def validate_email(email: str):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValidationError("L'adresse email est invalide.")

def validate_password(password: str):
    if len(password) < 8:
        raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")

def validate_role(role: str):
    valid_roles = ['COMMERCIAL', 'SUPPORT', 'GESTION']
    if role.upper() not in valid_roles:
        raise ValidationError(f"Le rôle doit être l'un de : {', '.join(valid_roles)}.")