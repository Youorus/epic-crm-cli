# cli/helpers/session.py

import os
import requests
import jwt
from getpass import getpass
from datetime import datetime, timezone
from typing import Optional, Any
from urllib.parse import urljoin

# 🔧 Utilise la config centralisée pour construire les URLs
try:
    from cli.utils.config import (
        API_BASE_URL,            # ex: "http://127.0.0.1:8000/api/"
        JWT_CREATE_URL,          # ex: ".../auth/jwt/create/"
        JWT_REFRESH_URL,         # ex: ".../auth/jwt/refresh/"
        ME_URL,                  # ex: ".../users/me/"
        url as build_url,        # concat propre si besoin
    )
except Exception:
    # Fallback minimal si la config n'est pas importable
    _RAW = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/")
    API_BASE_URL = _RAW.rstrip("/") + "/"
    def build_url(path: str) -> str:
        return API_BASE_URL + path.lstrip("/")
    JWT_CREATE_URL  = build_url("auth/jwt/create/")   # 🔴 note le slash final
    JWT_REFRESH_URL = build_url("auth/jwt/refresh/")
    ME_URL          = build_url("users/me/")

# 📁 Fichier local pour stocker les tokens JWT
TOKEN_FILE = os.path.expanduser("~/.epic_crm_token")

# ⏱️ Timeout réseau par défaut (secondes)
DEFAULT_TIMEOUT = 10


class Session:
    """
    Session HTTP avec gestion JWT (login + refresh) et helpers HTTP.
    - Stocke access/refresh localement (~/.epic_crm_token)
    - Rafraîchit automatiquement l'access token si expiré
    - Expose get/post/put/patch/delete avec en-têtes Authorization
    """

    def __init__(self):
        self.tokens: dict[str, str] = {}   # {"access": "...", "refresh": "..."}
        self.user: dict | None = None      # Informations utilisateur connecté
        self._load_tokens()

    # -----------------------
    # Authentification
    # -----------------------
    def login_prompt(self) -> bool:
        """Demande username/password, enregistre les tokens si succès et charge le profil."""
        print("\n=== Connexion ===")
        username = input("Nom d'utilisateur : ").strip()
        password = getpass("Mot de passe : ")

        try:
            r = requests.post(
                JWT_CREATE_URL,  # ✅ URL avec slash final
                json={"username": username, "password": password},
                timeout=DEFAULT_TIMEOUT,
            )
        except requests.RequestException as e:
            print("❌ Erreur de connexion à l'API :", e)
            return False

        if r.status_code == 200:
            self.tokens = r.json() or {}
            self._save_tokens()

            # Charge immédiatement l'utilisateur connecté
            if self.load_current_user():
                print(f"✅ Connecté en tant que {self.user.get('username')} ({self.user.get('role')})")
            else:
                print("⚠️ Connecté, mais impossible de récupérer le profil utilisateur.")
            return True

        print(f"❌ Échec ({r.status_code}) : {r.text}")
        return False

    def _decode_access(self) -> dict:
        """Décode l'access token sans vérifier la signature (lecture des claims)."""
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
        Essaie d'abord /users/me/, sinon fallback via user_id extrait du JWT.
        """
        # 1) /users/me/
        try:
            resp = self.get(ME_URL, absolute=True)
            if 200 <= resp.status_code < 300:
                self.user = resp.json()
                return True
        except Exception:
            # on tente le fallback
            pass

        # 2) Fallback via user_id du token
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
        """Retourne True si l'access token est expiré (ou manquant)."""
        access = self.tokens.get("access")
        if not access:
            return True
        try:
            payload = jwt.decode(access, options={"verify_signature": False, "verify_exp": False})
            exp = payload.get("exp")
            if not exp:
                # pas d’exp → on considère valide
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
                JWT_REFRESH_URL,  # ✅ URL avec slash final
                json={"refresh": refresh},
                timeout=DEFAULT_TIMEOUT,
            )
        except requests.RequestException:
            return False

        if r.status_code == 200:
            self.tokens["access"] = (r.json() or {}).get("access")
            self._save_tokens()
            print("♻️ Access token rafraîchi.")
            return True
        return False

    def ensure_access_token(self) -> str:
        """
        Retourne un access token valide, essaye de rafraîchir si expiré.
        Si aucun token n’est présent, tente un login interactif.
        """
        if not self.tokens.get("access"):
            # Pas de token → on tente de se connecter
            if not self.login_prompt():
                raise RuntimeError("❌ Non authentifié (aucun token).")
        if not self._is_access_expired():
            return self.tokens["access"]
        if self._refresh_access_token():
            return self.tokens["access"]
        # Refresh échoué → on tente un login direct
        print("ℹ️ Rafraîchissement impossible, nouvelle authentification requise.")
        if self.login_prompt():
            return self.tokens["access"]
        raise RuntimeError("❌ Impossible d’obtenir un access token valide.")

    def _save_tokens(self) -> None:
        """Sauvegarde access/refresh dans un fichier local (permissions restreintes)."""
        try:
            with open(TOKEN_FILE, "w") as f:
                f.write(f"{self.tokens.get('access','')}\n{self.tokens.get('refresh','')}")
            # Restreint les droits du fichier (Unix)
            try:
                os.chmod(TOKEN_FILE, 0o600)
            except Exception:
                pass
        except Exception as e:
            print(f"⚠️ Impossible d’écrire le fichier token ({TOKEN_FILE}) : {e}")

    def _load_tokens(self) -> None:
        """Charge les tokens depuis le disque si présents."""
        if not os.path.exists(TOKEN_FILE):
            return
        try:
            with open(TOKEN_FILE, "r") as f:
                lines = f.read().strip().split("\n")
                if len(lines) >= 2:
                    self.tokens = {"access": lines[0], "refresh": lines[1]}
        except Exception:
            # fichier corrompu → on ignore
            self.tokens = {}

    def clear_tokens(self) -> None:
        """Supprime les tokens et le fichier associé."""
        self.tokens.clear()
        if os.path.exists(TOKEN_FILE):
            try:
                os.remove(TOKEN_FILE)
            except Exception:
                pass

    # -----------------------
    # Helpers HTTP
    # -----------------------
    def _headers(self) -> dict:
        """Construit les en-têtes avec Authorization."""
        return {
            "Authorization": f"Bearer {self.ensure_access_token()}",
            "Content-Type": "application/json",
        }

    def _full_url(self, path: str) -> str:
        """
        Construit l'URL complète à partir d'un chemin relatif (ex: 'clients/').
        Si path est déjà une URL absolue, on la retourne telle quelle via absolute=True
        dans les wrappers (voir self.get(..., absolute=True)).
        """
        return urljoin(API_BASE_URL, path)

    def get(self, path: str, *, absolute: bool = False, **kwargs) -> requests.Response:
        url = path if absolute else self._full_url(path)
        return requests.get(url, headers=self._headers(), timeout=DEFAULT_TIMEOUT, **kwargs)

    def post(self, path: str, json: Any = None, *, absolute: bool = False, **kwargs) -> requests.Response:
        url = path if absolute else self._full_url(path)
        return requests.post(url, headers=self._headers(), json=json, timeout=DEFAULT_TIMEOUT, **kwargs)

    def put(self, path: str, json: Any = None, *, absolute: bool = False, **kwargs) -> requests.Response:
        url = path if absolute else self._full_url(path)
        return requests.put(url, headers=self._headers(), json=json, timeout=DEFAULT_TIMEOUT, **kwargs)

    def patch(self, path: str, json: Any = None, *, absolute: bool = False, **kwargs) -> requests.Response:
        url = path if absolute else self._full_url(path)
        return requests.patch(url, headers=self._headers(), json=json, timeout=DEFAULT_TIMEOUT, **kwargs)

    def delete(self, path: str, *, absolute: bool = False, **kwargs) -> requests.Response:
        url = path if absolute else self._full_url(path)
        return requests.delete(url, headers=self._headers(), timeout=DEFAULT_TIMEOUT, **kwargs)

    # -----------------------
    # Utils réponses
    # -----------------------
    @staticmethod
    def ok_json(resp: requests.Response) -> Optional[Any]:
        """
        Retourne le JSON si succès HTTP 2xx, sinon affiche l'erreur et retourne None.
        """
        if 200 <= resp.status_code < 300:
            try:
                return resp.json()
            except ValueError:
                print("⚠ Réponse reçue mais pas un JSON valide.")
                return None

        print(f"❌ Erreur HTTP {resp.status_code} sur {getattr(resp, 'url', '<inconnu>')}")
        try:
            print("📨", resp.json())
        except ValueError:
            print("📨", resp.text)
        return None


# Instance globale réutilisable
session = Session()