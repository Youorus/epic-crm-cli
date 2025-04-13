import requests

API_URL = 'http://127.0.0.1:8000/api/'
TOKEN_URL = API_URL + 'token/'


def login():
    print("=== Connexion ===")
    username = input("Nom d'utilisateur : ")
    password = input("Mot de passe : ")

    response = requests.post(TOKEN_URL, data={
        'username': username,
        'password': password
    })

    if response.status_code == 200:
        token = response.json()['access']
        print("✅ Connexion réussie")
        return token
    else:
        print("❌ Identifiants incorrects")
        return None


def get_current_user(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(API_URL + 'me/', headers=headers)

    if response.status_code == 200:
        return response.json()
    return None


# Optionnel : pour décoder le token sans le valider (utile pour obtenir l'identité)
import jwt


def decode_token(token):
    try:
        return jwt.decode(token, options={"verify_signature": False}, algorithms=["HS256"])
    except Exception:
        return {}