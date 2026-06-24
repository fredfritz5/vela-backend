import os
import base64
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.getenv("DARAJA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("DARAJA_CONSUMER_SECRET")
ENVIRONMENT = os.getenv("DARAJA_ENVIRONMENT", "sandbox")

BASE_URL = (
    "https://sandbox.safaricom.co.ke"
    if ENVIRONMENT == "sandbox"
    else "https://api.safaricom.co.ke"
)

_cached_token = None
_token_expiry = None

def get_access_token() -> str:
    global _cached_token, _token_expiry

    if _cached_token and _token_expiry and datetime.now() < _token_expiry:
        return _cached_token
    
    credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    response = httpx.get(
        f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
        headers={"Authorization": f"Basic {encoded_credentials}"},
    )
    response.raise_for_status()
    data = response.json()

    _cached_token = data["access_token"]
    _token_expiry = datetime.now() + timedelta(minutes=55)

    return _cached_token
