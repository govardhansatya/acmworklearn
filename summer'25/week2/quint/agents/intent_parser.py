import os
from groq import Groq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GEMINI_API_KEY"))

from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

def parse_intent_and_entities(prompt: str):
    """Parse the user's prompt to determine the intent and extract entities."""
    response = client.chat.completions.create(
        model="llama3-8b-8192",  # use 'llama3-70b-8192' if needed
        messages=[
            {"role": "system", "content": "You are an assistant that extracts intent and relevant entities."},
            {"role": "user", "content": prompt}
        ],
        prompt=f"""
        You are an AI assistant. Analyze this instruction: "{prompt}"
        Return JSON with:
        - intent (e.g., schedule_meeting, send_alert, send_whatsapp, wish_birthday, write_code, fetch_linkedin)
        - person
        - time
        - platform
        - message
        - task_topic
        """,
        metadata={"mode": "structured"}
    )
    
    return response.get("json", {})
    parsed = response.choices[0].message.content.strip()
    return parsed

