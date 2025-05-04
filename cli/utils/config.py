import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")  # Exemple : http://127.0.0.1:8000/api/

# Auth
TOKEN_URL = f"{API_BASE_URL}token/"
REFRESH_URL = f"{API_BASE_URL}token/refresh/"
ME_URL = f"{API_BASE_URL}me/"

# Clients
CLIENT_URL = f"{API_BASE_URL}clients/"

# Contracts
CONTRACT_URL = f"{API_BASE_URL}contracts/"

# Events
EVENT_URL = f"{API_BASE_URL}commercial/events/"

GESTION_CONTRACT_URL = f"{API_BASE_URL}gestion/contracts/"

COMMERCIAL_CONTRACT_URL = f"{API_BASE_URL}commercial/contracts/"

# Users (si admin gestion des utilisateurs par exemple)
USER_URL = f"{API_BASE_URL}users/"
