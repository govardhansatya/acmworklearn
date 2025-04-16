import streamlit as st

from auth.google_auth import authorize_google_account, logout

def sidebar():
    st.sidebar.title("🧠 Personal Assistant")

    user_email, token, action = authorize_google_account()
    if not user_email:
        st.stop()

    menu_choice = st.sidebar.selectbox("Select", ["Chat", "Settings"])
    return user_email, token, menu_choice

# ui/dashboard.py
# dashboard.py
import streamlit as st
from auth import authorize_google_account, logout

import streamlit as st
from auth.google_auth import authorize_google_account
from auth.access_control import check_access
from backend import calendar

# Function to initialize Google Calendar connection
def init_google_calendar():
    # Check authentication
    if not check_access():
        return
    
    # If authenticated, display calendar functionality
    st.success("You are authenticated!")
    calendar.display_upcoming_events()

# Call Google authentication function
authorize_google_account()

# Initialize Google Calendar once authenticated
init_google_calendar()
from auth.google_auth import logout

if st.sidebar.button("Logout"):
    logout()
    st.experimental_rerun() 
    st.session_state.clear()
    st.experimental_rerun()
    st.sidebar.success("Logged out successfully!")