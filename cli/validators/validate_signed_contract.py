from cli.validators.exceptions import ValidationError

def validate_signed_contract(contract_id: int, contracts: list):
    for contract in contracts:
        if contract['id'] == contract_id:
            if not contract.get('is_signed', False):
                raise ValidationError("❌ Ce contrat n'est pas encore signé.")
            return
    raise ValidationError("❌ Contrat introuvable.")