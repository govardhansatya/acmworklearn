from langchain.agents import tool
from backend import calendar, birthdays, alerts, linkedin, code_writer, whatsapp

@tool
def schedule_meeting_tool(user: str, content: str):
    """Schedule a meeting using Google Calendar."""
    return f"Meeting scheduling triggered for {user}. Please check the UI."

@tool
def birthday_checker_tool(user: str, content: str):
    """Check today's birthdays and wish them."""
    return f"Birthday check initiated for {user}. Check UI for local contacts."

@tool
def alert_tool(user: str, content: str):
    """Create or view alerts."""
    return f"Alert setup for {user} initiated."

@tool
def linkedin_fetch_tool(user: str, content: str):
    """Fetch latest LinkedIn posts based on keyword."""
    return f"LinkedIn fetch started. Visit LinkedIn tab to see matches."

@tool
def code_writer_tool(user: str, content: str):
    """Write or generate code based on prompt."""
    return code_writer.generate_code(content)

@tool
def send_message_tool(user: str, content: str):
    """Send a WhatsApp message."""
    try:
        phone, message = content.split(":", 1)
        success = whatsapp.send_whatsapp(phone.strip(), message.strip())
        return "✅ Message sent!" if success else "❌ Failed to send."
    except Exception:
        return "Invalid format. Use: phone: message"
