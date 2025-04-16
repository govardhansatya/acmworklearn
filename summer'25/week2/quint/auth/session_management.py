# auth/session_management.py

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import streamlit as st

TOKEN_FILE = "auth/token.json"

def load_credentials():
    """Load stored credentials or start the OAuth flow if not present."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as token:
            creds = Credentials.from_authorized_user_info(json.load(token))
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
            return creds
    return None

def save_credentials(creds):
    """Save credentials to a file."""
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())

def is_authenticated():
    """Check if the user is authenticated."""
    return os.path.exists(TOKEN_FILE)
