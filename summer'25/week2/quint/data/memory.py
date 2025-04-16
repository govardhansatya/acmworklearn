from data.models import Conversation
from data.db import SessionLocal

def save_conversation(user_msg, assistant_resp):
    db = SessionLocal()
    convo = Conversation(user_message=user_msg, assistant_response=assistant_resp)
    db.add(convo)
    db.commit()
    db.close()

def get_recent_history(n=5):
    db = SessionLocal()
    history = db.query(Conversation).order_by(Conversation.timestamp.desc()).limit(n).all()
    db.close()
    return [(h.user_message, h.assistant_response) for h in reversed(history)]
