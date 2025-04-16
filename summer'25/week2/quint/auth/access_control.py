# auth/access_control.py

import streamlit as st
from auth.session_management import is_authenticated

def check_access():
    """Check if the user is authenticated. If not, prompt for authentication."""
    if not is_authenticated():
        st.error("You must authenticate first!")
        return False
    return True
