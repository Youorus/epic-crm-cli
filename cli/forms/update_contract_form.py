from cli.forms.contract_update_form import create_contract_form


def update_contract_form():
    contract_id = input("ID du contrat à modifier : ").strip()
    data = create_contract_form()
    return contract_id, data