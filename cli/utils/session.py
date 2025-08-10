# cli/helpers/session.py

import os
import requests
import jwt
from getpass import getpass
from datetime import datetime, timezone
from typing import Optional, Any
from urllib.parse import urljoin

# Base API depuis .env, avec fallback
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/").rstrip("/") + "/"

# Fichier local pour stocker les tokens JWT
TOKEN_FILE = os.path.expanduser("~/.epic_crm_token")


class Session:
    """Session HTTP avec gestion JWT (login + refresh) et helpers HTTP."""

    def __init__(self):
        self.tokens: dict[str, str] = {}   # {"access": "...", "refresh": "..."}
        self.user: dict | None = None      # Informations utilisateur connecté
        self._load_tokens()

    # -----------------------
    # Authentification
    # -----------------------
    def login_prompt(self) -> bool:
        """Demande username/password, enregistre les tokens si succès."""
        print("\n=== Connexion ===")
        username = input("Nom d'utilisateur : ").strip()
        password = getpass("Mot de passe : ")

        try:
            r = requests.post(
                urljoin(API_BASE_URL, "auth/jwt/create"),
                json={"username": username, "password": password},
                timeout=10
            )
            if r.status_code == 200:
                self.tokens = r.json()
                self._save_tokens()

                # Charge immédiatement l'utilisateur connecté
                if self.load_current_user():
                    print(f"✅ Connecté en tant que {self.user.get('username')} ({self.user.get('role')})")
                else:
                    print("⚠️ Connecté, mais impossible de récupérer le profil utilisateur.")
                return True

            print(f"❌ Échec ({r.status_code}) : {r.text}")
        except requests.RequestException as e:
            print("❌ Erreur de connexion à l'API :", e)
        return False

    def _decode_access(self) -> dict:
        """Décode l'access token sans vérifier la signature."""
        access = self.tokens.get("access")
        if not access:
            return {}
        try:
            return jwt.decode(access, options={"verify_signature": False})
        except Exception:
            return {}

    def load_current_user(self) -> bool:
        """
        Récupère et mémorise l'utilisateur courant dans self.user.
        Essaie d'abord /users/me/, sinon fallback via user_id du JWT.
        """
        try:
            resp = self.get("users/me/")
            if 200 <= resp.status_code < 300:
                self.user = resp.json()
                return True
        except Exception:
            pass

        payload = self._decode_access()
        uid = payload.get("user_id")
        if not uid:
            return False

        resp = self.get(f"users/{uid}/")
        if 200 <= resp.status_code < 300:
            self.user = resp.json()
            return True

        return False

    # -----------------------
    # Gestion des tokens
    # -----------------------
    def _is_access_expired(self) -> bool:
        """Vérifie si l'access token est expiré."""
        access = self.tokens.get("access")
        if not access:
            return True
        try:
            payload = jwt.decode(access, options={"verify_signature": False, "verify_exp": False})
            exp = payload.get("exp")
            if not exp:
                return False
            return datetime.now(timezone.utc).timestamp() >= exp
        except Exception:
            return True

    def _refresh_access_token(self) -> bool:
        """Tente un refresh, retourne True si succès."""
        refresh = self.tokens.get("refresh")
        if not refresh:
            return False
        try:
            r = requests.post(
                urljoin(API_BASE_URL, "auth/jwt/refresh"),
                json={"refresh": refresh},
                timeout=10
            )
            if r.status_code == 200:
                self.tokens["access"] = r.json().get("access")
                self._save_tokens()
                print("♻️ Access token rafraîchi.")
                return True
            return False
        except requests.RequestException:
            return False

    def ensure_access_token(self) -> str:
        """Retourne un access token valide, refresh si nécessaire."""
        if not self._is_access_expired():
            return self.tokens["access"]
        if self._refresh_access_token():
            return self.tokens["access"]
        raise RuntimeError("❌ Impossible de rafraîchir le token.")

    def _save_tokens(self) -> None:
        """Sauvegarde les tokens en local."""
        with open(TOKEN_FILE, "w") as f:
            f.write(f"{self.tokens.get('access','')}\n{self.tokens.get('refresh','')}")

    def _load_tokens(self) -> None:
        """Charge les tokens depuis le disque."""
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r") as f:
                    lines = f.read().strip().split("\n")
                    if len(lines) >= 2:
                        self.tokens = {"access": lines[0], "refresh": lines[1]}
            except Exception:
                pass

    def clear_tokens(self) -> None:
        """Supprime les tokens et le fichier associé."""
        self.tokens.clear()
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)

    # -----------------------
    # Helpers HTTP
    # -----------------------
    def _headers(self) -> dict:
        """Retourne les headers avec Authorization."""
        return {
            "Authorization": f"Bearer {self.ensure_access_token()}",
            "Content-Type": "application/json"
        }

    def _full_url(self, path: str) -> str:
        """Construit l'URL complète, même si path est relatif."""
        return urljoin(API_BASE_URL, path)

    def get(self, path: str, **kwargs) -> requests.Response:
        return requests.get(self._full_url(path), headers=self._headers(), timeout=10, **kwargs)

    def post(self, path: str, json: Any = None, **kwargs) -> requests.Response:
        return requests.post(self._full_url(path), headers=self._headers(), json=json, timeout=10, **kwargs)

    def put(self, path: str, json: Any = None, **kwargs) -> requests.Response:
        return requests.put(self._full_url(path), headers=self._headers(), json=json, timeout=10, **kwargs)

    def patch(self, path: str, json: Any = None, **kwargs) -> requests.Response:
        return requests.patch(self._full_url(path), headers=self._headers(), json=json, timeout=10, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return requests.delete(self._full_url(path), headers=self._headers(), timeout=10, **kwargs)

    # -----------------------
    # Utils réponses
    # -----------------------
    @staticmethod
    def ok_json(resp: requests.Response) -> Optional[Any]:
        """Retourne le JSON si succès HTTP, sinon affiche l'erreur."""
        if 200 <= resp.status_code < 300:
            try:
                return resp.json()
            except ValueError:
                print("⚠ Réponse reçue mais pas un JSON valide.")
                return None
        print(f"❌ Erreur HTTP {resp.status_code}")
        try:
            print("📨", resp.json())
        except ValueError:
            print("📨", resp.text)
        return None


# Instance globale réutilisable
session = Session()