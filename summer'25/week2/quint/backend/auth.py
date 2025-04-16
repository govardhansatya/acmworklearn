import jwt
from datetime import datetime, timedelta
from config.settings import SECRET_KEY

def generate_token(username: str):
    payload = {
        "user": username,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("user")
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
import os
import json
from google.oauth2.credentials import Credentials

CREDENTIALS_PATH = "auth/token.json"

def get_google_credentials():
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError("Google credentials not found. Please authenticate first.")
    with open(CREDENTIALS_PATH, "r") as file:
        token_data = json.load(file)
    return Credentials.from_authorized_user_info(token_data)

