from cli.validators.exceptions import ValidationError


def validate_signed_input(value: str):
    if value.lower() not in ["true", "false"]:
        raise ValidationError("Valeur attendue : true ou false.")
    return value.lower() == "true"