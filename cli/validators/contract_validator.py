from cli.validators.exceptions import ValidationError


def validate_contract_id(value: str, contracts: list) -> int:
    if not value.isdigit():
        raise ValidationError("❌ L’ID du contrat doit être un nombre entier.")

    contract_id = int(value)
    if not any(c['id'] == contract_id for c in contracts):
        raise ValidationError("❌ Ce contrat n'existe pas dans la liste fournie.")

    return contract_id