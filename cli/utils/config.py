# cli/utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
CLIENT_URL = f"{API_BASE_URL}clients/"
CONTRACT_URL = f"{API_BASE_URL}contracts/"
EVENT_URL = f"{API_BASE_URL}events/"