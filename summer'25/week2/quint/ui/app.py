import streamlit as st
from ui.dashboard import sidebar
from agents.core_crew import route_prompt
from backend import calendar, birthdays, alerts, linkedin
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


st.set_page_config(page_title="AI Personal Assistant", layout="wide")


import streamlit as st
from ui.dashboard import sidebar
from agents.core_crew import route_prompt

st.title("🤖 AI Personal Assistant")

user_email, token, action = sidebar()

if action == "Chat":
    prompt = st.text_input("What do you want to do?")
    if prompt:
        response = route_prompt(prompt, {"email": user_email, "token": token})
        st.write(response)


# Add other menu options as needed
import streamlit as st
from ui.dashboard import sidebar
from auth.google_auth import auth_page
from agents.core_crew import route_prompt

menu_choice = sidebar()

if menu_choice == "Login":
    auth_page()

elif menu_choice == "Assistant":
    if not st.session_state.get("is_logged_in"):
        st.warning("🔐 Please log in first.")
    else:
        st.title("🧠 Personal Assistant")
        user = st.text_input("Your name")
        prompt = st.text_area("What can I help you with?")
        if st.button("Run") and prompt:
            response = route_prompt(prompt, {"username": user})
            st.markdown("### Response")
            st.write(response)
from auth.google_auth import logout

if st.sidebar.button("Logout"):
    logout()
    st.experimental_rerun()  # Optional: Refresh app to enforce logout
# app.py
import streamlit as st
from dashboard import sidebar
from googleapiclient.discovery import build
from datetime import datetime

def list_upcoming_events(creds, max_results=5):
    service = build("calendar", "v3", credentials=creds)
    now = datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(
        calendarId="primary", timeMin=now,
        maxResults=max_results, singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])
    if not events:
        st.info("No upcoming events found.")
    else:
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            st.write(f"📅 {event['summary']} at {start}")

def create_event_ui(creds):
    st.subheader("📌 Create New Event")
    with st.form("event_form"):
        title = st.text_input("Event Title")
        start_time = st.text_input("Start Time (YYYY-MM-DDTHH:MM:SS)")
        end_time = st.text_input("End Time (YYYY-MM-DDTHH:MM:SS)")
        description = st.text_area("Description")
        submitted = st.form_submit_button("Create Event")
        if submitted:
            service = build("calendar", "v3", credentials=creds)
            event = {
                "summary": title,
                "description": description,
                "start": {"dateTime": start_time, "timeZone": "UTC"},
                "end": {"dateTime": end_time, "timeZone": "UTC"},
            }
            created_event = service.events().insert(calendarId="primary", body=event).execute()
            st.success(f"✅ Event created: {created_event['summary']}")

# MAIN APP FLOW
user_email, token, action = sidebar()

if action == "Schedule":
    creds = st.session_state.get("creds")
    if creds:
        list_upcoming_events(creds)
        create_event_ui(creds)
# app.py (continued)
import streamlit as st
from dashboard import sidebar
from your_agent_backend import run_assistant  # Replace with your bot logic

# Get authentication + action
user_email, token, action = sidebar()

# Main Chat Input Interface
if user_email and action != "Logout":
    st.title("🤖 Your Assistant")
    user_input = st.chat_input("Type your message here...")

    if user_input:
        with st.spinner("Thinking..."):
            response = run_assistant(user_input, user_email=user_email)
        st.chat_message("user").write(user_input)
        st.chat_message("assistant").write(response)
