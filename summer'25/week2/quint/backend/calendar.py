import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config.settings import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
import os
import json

# Path to your token.json for OAuth tokens
TOKEN_PATH = "auth/token.json"

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/calendar'])
    else:
        raise Exception("No token found. Please authenticate first.")
    return build("calendar", "v3", credentials=creds)

def schedule_event(summary, start_time_str, duration_minutes=60, timezone="Asia/Kolkata"):
    service = get_calendar_service()

    start_datetime = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
    end_datetime = start_datetime + datetime.timedelta(minutes=duration_minutes)

    event = {
        "summary": summary,
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": timezone,
        },
    }

    event = service.events().insert(calendarId="primary", body=event).execute()
    return f"✅ Event created: {event.get('htmlLink')}"
