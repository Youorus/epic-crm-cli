# cli/helpers/api.py
import os
import requests
import jwt
from getpass import getpass
from datetime import datetime, timezone

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

JWT_CREATE = f"{API_BASE_URL}/api/auth/jwt/create"
JWT_REFRESH = f"{API_BASE_URL}/api/auth/jwt/refresh"
JWT_VERIFY  = f"{API_BASE_URL}/api/auth/jwt/verify"
USERS_DETAIL = f"{API_BASE_URL}/api/users/{{user_id}}"

def prompt_login() -> dict | None:
    """
    Demande username/password et récupère {access, refresh} depuis l’API.
    Retourne None si échec.
    """
    print("\n=== Connexion ===")
    username = input("Nom d'utilisateur : ").strip()
    password = getpass("Mot de passe : ")

    try:
        r = requests.post(JWT_CREATE, json={"username": username, "password": password}, timeout=10)
        if r.status_code == 200:
            print("✅ Authentification réussie.")
            return r.json()  # {"access": "...", "refresh": "..."}
        print(f"❌ Échec ({r.status_code}) : {r.text}")
    except requests.RequestException as e:
        print("❌ Erreur de connexion à l'API :", e)
    return None


def _is_access_expired(access_token: str) -> bool:
    """
    Vérifie localement si le token est expiré (lit 'exp' sans vérifier la signature).
    """
    try:
        payload = jwt.decode(access_token, options={"verify_signature": False, "verify_exp": False})
        exp = payload.get("exp")
        if not exp:
            return False
        return datetime.now(timezone.utc).timestamp() >= exp
    except Exception:
        return True


def ensure_access_token(tokens: dict) -> str:
    """
    Retourne un access token valide; si expiré, tente un refresh.
    Modifie tokens['access'] si rafraîchi.
    """
    access = tokens.get("access")
    refresh = tokens.get("refresh")

    if access and not _is_access_expired(access):
        return access

    if not refresh:
        raise RuntimeError("Pas de refresh token pour renouveler l'access token.")

    r = requests.post(JWT_REFRESH, json={"refresh": refresh}, timeout=10)
    if r.status_code == 200:
        tokens["access"] = r.json().get("access")
        print("♻️ Access token rafraîchi.")
        return tokens["access"]
    raise RuntimeError(f"Refresh échoué ({r.status_code}) : {r.text}")


def auth_headers(tokens: dict) -> dict:
    """
    Construit les headers Authorization à partir du token (refresh si besoin).
    """
    access = ensure_access_token(tokens)
    return {"Authorization": f"Bearer {access}"}


def get_current_user(tokens: dict) -> dict | None:
    """
    Lit user_id dans l'access token et récupère l'utilisateur via /api/users/{id}/
    """
    access = ensure_access_token(tokens)
    try:
        payload = jwt.decode(access, options={"verify_signature": False})
        user_id = payload.get("user_id")
    except Exception:
        print("❌ Token invalide.")
        return None

    if not user_id:
        print("❌ 'user_id' manquant dans le token.")
        return None

    headers = {"Authorization": f"Bearer {access}"}
    r = requests.get(USERS_DETAIL.format(user_id=user_id), headers=headers, timeout=10)
    if r.status_code == 200:
        return r.json()
    print(f"❌ Récupération utilisateur impossible ({r.status_code}) : {r.text}")
    return None


# Helpers génériques pour tes futurs appels API
def api_get(path: str, tokens: dict, **kwargs):
    headers = {**auth_headers(tokens), **kwargs.pop("headers", {})}
    return requests.get(f"{API_BASE_URL}{path}", headers=headers, timeout=kwargs.pop("timeout", 10), **kwargs)

def api_post(path: str, tokens: dict, json=None, **kwargs):
    headers = {**auth_headers(tokens), **kwargs.pop("headers", {})}
    return requests.post(f"{API_BASE_URL}{path}", headers=headers, json=json, timeout=kwargs.pop("timeout", 10), **kwargs)

def api_put(path: str, tokens: dict, json=None, **kwargs):
    headers = {**auth_headers(tokens), **kwargs.pop("headers", {})}
    return requests.put(f"{API_BASE_URL}{path}", headers=headers, json=json, timeout=kwargs.pop("timeout", 10), **kwargs)

def api_patch(path: str, tokens: dict, json=None, **kwargs):
    headers = {**auth_headers(tokens), **kwargs.pop("headers", {})}
    return requests.patch(f"{API_BASE_URL}{path}", headers=headers, json=json, timeout=kwargs.pop("timeout", 10), **kwargs)

def api_delete(path: str, tokens: dict, **kwargs):
    headers = {**auth_headers(tokens), **kwargs.pop("headers", {})}
    return requests.delete(f"{API_BASE_URL}{path}", headers=headers, timeout=kwargs.pop("timeout", 10), **kwargs)