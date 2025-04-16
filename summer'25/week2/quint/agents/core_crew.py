from agents.intent_parser import parse_intent_and_entities
from backend import calendar, alerts, birthdays, whatsapp, linkedin
from datetime import datetime, timedelta
import dateparser  # Make sure this is installed

def route_prompt(prompt: str, session_info: dict):
    user_token = session_info.get("token")
    email = session_info.get("email")
    parsed = parse_intent_and_entities(prompt)
    intent = parsed.get("intent")
    entities = parsed.get("entities")
    

    try:
        if intent == "schedule_meeting":
            date_time = dateparser.parse(entities["datetime_info"])
            if not date_time:
                return "Couldn't understand the meeting time. Please try again."

            start = date_time.isoformat()
            end = (date_time + timedelta(hours=1)).isoformat()

            event_link = calendar.create_event(
                summary=entities["summary"],
                description=entities["description"],
                start_time=start,
                end_time=end
            )
            return f"✅ Meeting scheduled successfully: [View in Calendar]({event_link})"
        elif intent == "send_alert":
            return alerts.set_alert(
                message=parsed.get("message"),
                time=parsed.get("time")
            )
        elif intent == "send_whatsapp":
            return whatsapp.send_message(
                contact=parsed.get("person"),
                message=parsed.get("message")
            )
        elif intent == "wish_birthday":
            return birthdays.auto_wish(
                name=parsed.get("person"),
                platform="whatsapp"
            )
        elif intent == "fetch_linkedin":
            return linkedin.search_posts(
                keyword=parsed.get("task_topic")
            )
        else:
            return "I couldn’t match the task type. Please clarify."

    except Exception as e:
        return f"❌ Failed to process: {str(e)}"
