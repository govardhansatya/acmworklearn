import requests
from config.settings import WHATSAPP_TOKEN

def send_whatsapp(phone_number, message):
    url = "https://graph.facebook.com/v17.0/PHONE_NUMBER_ID/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200
