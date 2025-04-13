from cli.validators.exceptions import ValidationError


def validate_attendees(value: str):
    try:
        n = int(value)
        if n <= 0:
            raise ValidationError("Le nombre de participants doit être positif.")
        return n
    except ValueError:
        raise ValidationError("Veuillez entrer un nombre entier valide.")
