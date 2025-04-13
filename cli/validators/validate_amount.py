from cli.validators.exceptions import ValidationError


def validate_amount(amount: str):
    try:
        value = float(amount)
        if value < 0:
            raise ValidationError("Le montant ne peut pas être négatif.")
        return value
    except ValueError:
        raise ValidationError("Veuillez entrer un montant valide (ex: 1000.00).")