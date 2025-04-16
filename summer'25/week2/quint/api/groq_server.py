from groq import Groq
from backend.auth import decode_token
from agents.core_crew import route_prompt

groq_app = Groq()

@groq_app.chat()
def handle_prompt(message, metadata):
    try:
        token = metadata.get("token")
        user = decode_token(token)
        result = route_prompt(message, {"username": user})
        return {"response": result}
    except Exception as e:
        return {"error": str(e)}
