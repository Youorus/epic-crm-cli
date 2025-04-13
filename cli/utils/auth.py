import jwt

from cli.services.authentification import api_login, api_get_current_user


def login():
    print("=== Connexion ===")
    username = input("Nom d'utilisateur : ")
    password = input("Mot de passe : ")

    response = api_login(username, password)

    if response is None:
        print("❌ Erreur de connexion au serveur.")
        return None

    if response.status_code == 200:
        token = response.json()['access']
        print("✅ Connexion réussie")
        return token
    else:
        print("❌ Identifiants incorrects")
        return None


def get_current_user(token: str):
    response = api_get_current_user(token)

    if response is None:
        print("❌ Le serveur est injoignable.")
        return None

    if response.status_code == 200:
        return response.json()
    else:
        print("❌ Impossible de récupérer les informations de l'utilisateur.")
        return None


def decode_token(token: str):
    try:
        return jwt.decode(token, options={"verify_signature": False}, algorithms=["HS256"])
    except Exception:
        return {}