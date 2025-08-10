# cli/utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Exemple attendu dans .env :
_RAW = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/")
API_BASE_URL = _RAW.rstrip("/") + "/"   # -> garantit exactement un "/" final

def url(path: str) -> str:
    """Construit une URL propre à partir de API_BASE_URL et d'un chemin relatif."""
    return API_BASE_URL + path.lstrip("/")

# --- Auth (SimpleJWT) ---
JWT_CREATE_URL  = url("auth/jwt/create")   # POST
JWT_REFRESH_URL = url("auth/jwt/refresh")  # POST
JWT_VERIFY_URL  = url("auth/jwt/verify")   # POST

# (Optionnel, seulement si tu as cet endpoint côté API)
ME_URL = url("users/me/")  # GET

# --- Ressources principales ---
CLIENT_URL   = url("clients/")    # GET/POST, etc.
CONTRACT_URL = url("contracts/")  # GET/POST/...
EVENT_URL    = url("events/")     # GET/POST/...
USER_URL     = url("users/")      # GET/POST/...

# --- Routes rôle-spécifiques (uniquement si tu les as réellement implémentées) ---
GESTION_EVENT_URL    = url("gestion/events/")
GESTION_CONTRACT_URL = url("gestion/contracts/")
COMMERCIAL_CONTRACT_URL = url("commercial/contracts/")
COMMERCIAL_EVENT_URL    = url("commercial/events/")