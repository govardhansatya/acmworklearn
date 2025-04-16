import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os, json

CLIENT_SECRETS_FILE = "auth/client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "auth/token.json"

def authorize_google_account():
    # Check if token already saved
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            creds_data = json.load(f)
        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
        user_email = creds.id_token.get("email") if creds.id_token else "Unknown"
        st.session_state["user_email"] = user_email
        st.session_state["google_token"] = creds.token
        return user_email, creds.token, "authenticated"

    # Extract ?code=... from URL after redirect
    query_params = st.experimental_get_query_params()
    code = query_params.get("code", [None])[0]

    if code:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri="http://localhost:8501",
        )
        flow.fetch_token(code=code)
        creds = flow.credentials

        # Save token
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

        st.session_state["user_email"] = creds.id_token.get("email")
        st.session_state["google_token"] = creds.token
        st.experimental_rerun()

    # If not authenticated, create a flow and show login link
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8501",
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    st.markdown(f"[Click here to log in with Google]({auth_url})")

    return None, None, "unauthenticated"
TOKEN_FILE = "auth/token.json"

def logout():
    """Securely log out the user by clearing session state and token file."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    st.session_state.clear()
    st.success("✅ You have been securely logged out.")